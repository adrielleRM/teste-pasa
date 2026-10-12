"""Gera as tabelas complementares do modelo Power BI (PBIP).

Os 6 CSVs do contrato em ``output/`` (gerados pelo notebook) NAO sao alterados.
Este script cria dois arquivos ADICIONAIS, necessarios para medidas que exigem
granularidade que o contrato nao expoe:

- ``despesa_vidas_faixa_mensal.csv``: despesa bruta/liquida e vidas por
  operadora x competencia x faixa etaria -> [Custo Per Capita Padronizado (Mix X)].
- ``migracao_planos_mensal.csv``: vidas e despesa liquida mensais dos dois planos
  envolvidos na transferencia de carteira -> [Variacao Vidas Organica %].

A logica replica as secoes 5.1/5.2 e 6.3/6.4 do notebook
``04_analise_consolidada_operadoras.ipynb`` e termina com barreiras
que conferem os numeros publicados (R$ 111,15; +0,52%; -0,84%).

Uso: python scripts/gerar_tabelas_complementares_powerbi.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

PASTA_RAIZ = Path(__file__).resolve().parents[1]
PASTA_DADOS = PASTA_RAIZ / "data"
PASTA_SAIDA = PASTA_RAIZ / "output"

LIMIAR_MOVIMENTO_PLANO = 1_000
LIMIAR_ESVAZIAMENTO = 0.05
CHAVES_FAIXA = ["Operadora", "data_ref", "faixa_etaria"]


def carregar():
    vidas = pd.read_csv(PASTA_DADOS / "Vidas.csv", parse_dates=["data_ref"])
    despesa = pd.read_csv(
        PASTA_DADOS / "Despesa.csv",
        usecols=["data_ref", "faixa_etaria", "Operadora", "Plano", "valor_bruto", "valor_coparticipacao"],
        parse_dates=["data_ref"],
    )
    despesa["despesa_liquida"] = despesa["valor_bruto"] - despesa["valor_coparticipacao"]
    return vidas, despesa


def tabela_faixa_mensal(vidas, despesa):
    tabela = (
        despesa.groupby(CHAVES_FAIXA, as_index=False)
        .agg(despesa_bruta=("valor_bruto", "sum"), despesa_liquida=("despesa_liquida", "sum"))
        .merge(vidas.groupby(CHAVES_FAIXA, as_index=False).agg(vidas=("Vidas", "sum")),
               on=CHAVES_FAIXA, how="outer", validate="one_to_one", indicator=True)
    )
    assert tabela["_merge"].eq("both").all(), "Segmentos sem correspondencia Despesa x Vidas."
    return tabela.drop(columns="_merge").sort_values(CHAVES_FAIXA)


def tabela_migracao(vidas, despesa):
    vidas_mes = vidas.groupby(["Operadora", "data_ref"])["Vidas"].sum()
    variacao = vidas_mes.groupby(level="Operadora").diff().abs()
    mes_quebra = variacao.groupby(level="Operadora").idxmax().str[1].mode().iat[0]
    mes_anterior = mes_quebra - pd.DateOffset(months=1)

    vidas_plano = vidas.groupby(["Operadora", "Plano", "data_ref"], as_index=False)["Vidas"].sum()
    matriz = vidas_plano.pivot_table(index=["Operadora", "Plano"], columns="data_ref",
                                     values="Vidas", aggfunc="sum", fill_value=0)
    mov = pd.DataFrame({"antes": matriz[mes_anterior], "depois": matriz[mes_quebra]})
    mov["variacao"] = mov["depois"] - mov["antes"]
    mov = mov[mov["variacao"].abs() >= LIMIAR_MOVIMENTO_PLANO].reset_index()
    encerrado = mov[mov["depois"] <= LIMIAR_ESVAZIAMENTO * mov["antes"]].sort_values("variacao").iloc[0]
    iniciado = mov[mov["antes"].eq(0)].sort_values("variacao").iloc[-1]
    papeis = {encerrado["Plano"]: "Plano de origem (esvaziado)",
              iniciado["Plano"]: "Plano de destino (iniciado)"}

    chaves = ["Operadora", "Plano", "data_ref"]
    despesa_plano = (despesa[despesa["Plano"].isin(papeis)]
                     .groupby(chaves, as_index=False)["despesa_liquida"].sum())
    painel = (vidas_plano[vidas_plano["Plano"].isin(papeis)]
              .merge(despesa_plano, on=chaves, how="outer")
              .rename(columns={"Vidas": "vidas"}))
    # Grade completa operadora/plano x 12 competencias (zeros explicitos facilitam o grafico).
    competencias = sorted(vidas["data_ref"].unique())
    grade = pd.MultiIndex.from_tuples(
        [(op, pl, c) for (op, pl) in painel[["Operadora", "Plano"]].drop_duplicates().itertuples(index=False)
         for c in competencias], names=chaves).to_frame(index=False)
    painel = grade.merge(painel, on=chaves, how="left").fillna({"vidas": 0, "despesa_liquida": 0})
    painel["vidas"] = painel["vidas"].astype("int64")
    painel["papel_migracao"] = painel["Plano"].map(papeis)
    painel["mes_migracao"] = mes_quebra
    return painel[["Operadora", "Plano", "papel_migracao", "data_ref", "mes_migracao",
                   "vidas", "despesa_liquida"]].sort_values(chaves)


def validar(faixa, migracao):
    # Per capita padronizado: custo por vida de cada faixa x mix etario da X (vidas-mes).
    custo = faixa.groupby(["Operadora", "faixa_etaria"])[["despesa_liquida", "vidas"]].sum()
    custo["custo_por_vida"] = custo["despesa_liquida"] / custo["vidas"]
    peso_x = custo.loc["Operadora X", "vidas"] / custo.loc["Operadora X", "vidas"].sum()
    padronizado_y = (custo.loc["Operadora Y", "custo_por_vida"] * peso_x).sum()
    assert round(padronizado_y, 2) == 111.15, padronizado_y

    # Conciliacao com o contrato (indicadores_mensais.csv).
    mensal = pd.read_csv(PASTA_SAIDA / "indicadores_mensais.csv", encoding="utf-8-sig",
                         parse_dates=["data_ref"]).set_index(["Operadora", "data_ref"])
    soma = faixa.groupby(["Operadora", "data_ref"])[["despesa_liquida", "vidas"]].sum()
    assert np.allclose(soma["despesa_liquida"], mensal.loc[soma.index, "despesa_liquida"])
    assert np.allclose(soma["vidas"], mensal.loc[soma.index, "vidas"])

    # Crescimento organico = vidas totais - vidas dos planos migrados (ponta a ponta).
    migr = migracao.groupby(["Operadora", "data_ref"])["vidas"].sum()
    organico = (mensal["vidas"] - migr.reindex(mensal.index, fill_value=0)).groupby(level="Operadora")
    variacao = (organico.last() / organico.first() - 1) * 100
    assert round(variacao["Operadora X"], 2) == 0.52 and round(variacao["Operadora Y"], 2) == -0.84, variacao
    print(f"OK - padronizado Y (mix X): R$ {padronizado_y:.2f} | organico: {variacao.round(2).to_dict()}")


def main():
    vidas, despesa = carregar()
    faixa = tabela_faixa_mensal(vidas, despesa)
    migracao = tabela_migracao(vidas, despesa)
    validar(faixa, migracao)
    for nome, tabela in {"despesa_vidas_faixa_mensal.csv": faixa,
                         "migracao_planos_mensal.csv": migracao}.items():
        saida = tabela.copy()
        for coluna in ("data_ref", "mes_migracao"):
            if coluna in saida:
                saida[coluna] = saida[coluna].dt.strftime("%Y-%m-%d")
        saida.to_csv(PASTA_SAIDA / nome, index=False, encoding="utf-8-sig")
        print(f"  - {nome}: {len(saida)} linhas x {saida.shape[1]} colunas")


if __name__ == "__main__":
    main()
