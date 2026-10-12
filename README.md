# Análise comparativa de operadoras — PASA

**Desafio técnico | Gerência de Inteligência de Mercado e Sinistro**
**Período:** agosto/2025 a julho/2026 (12 competências) · **Fontes:** Receita, Vidas e Despesa · **Operadoras:** X e Y

---

## 1. Resumo executivo

As duas operadoras **não são comparáveis pelos números brutos**. A Y é uma carteira envelhecida e de alta severidade, mas é mais barata que a X em 8 das 10 faixas etárias. A X é jovem, com custo por faixa mais alto nas idades adultas. Em jan/2026, um bloco de cerca de 10 mil vidas migrou da X para a Y, e não há receita da X na base para avaliar a sustentabilidade da maior carteira.

### Os 7 achados estratégicos — Evidência → Risco → Recomendação

| # | Achado | Evidência | Risco | Recomendação |
|---|---|---|---|---|
| 1 | **Transferência de carteira X → Y (jan/2026)** | O plano `340154BC84` da X (PA) cai de 10.110 para 8 vidas e nasce o plano `0F2726E6AC` da Y (PA) com 10.244 vidas e perfil etário 99,0% semelhante. Sem o bloco, X **+0,52%** e Y **−0,84%** (vs. −2,05% e +12,42% totais). | Ler o crescimento da Y como expansão comercial. O plano chega à Y sem receita na base (13,6% das vidas da Y) e a X segue pagando **R$ 0,95 mi** de cauda após a saída. | Confirmar a natureza contratual da operação, definir a responsabilidade pela cauda (IBNR) e obter a receita do plano. |
| 2 | **Custo per capita explicado pela idade** | Y R$ 261,54 × X R$ 124,39 por vida/mês (2,1×). Com a pirâmide etária da X, a Y custaria **R$ 111,15**: a idade explica 109,7% da diferença. Custo médio por item equivalente (X R$ 26,92; Y R$ 26,47). | Concluir que a Y é "ineficiente". O ponto de atenção real é a X, com custo 13% a 53% acima da Y entre 19 e 53 anos. | Adotar o **custo per capita padronizado por idade** como KPI; investigar utilização e protocolos da X nas faixas adultas. |
| 3 | **Concentração etária da Y** | Faixa 59+ = 48,51% das vidas e 78,39% da despesa bruta. Internação = 56,43% da despesa líquida (X: 45,96%). | Severidade alta e crônica; pressão estrutural de custo com o envelhecimento. | Gestão de crônicos e linhas de cuidado 60+, monitoramento de alto custo e reinternações, reajuste aderente à pirâmide. |
| 4 | **Mix assistencial da Y** | Medicamentos 28,26% e pacotes 21,42% da despesa bruta (X: 15,55% e 16,34%). | Exposição a medicamentos de alto custo e pacotes hospitalares mal precificados. | Auditoria de medicamentos especiais, autorização prévia por protocolo e renegociação de pacotes. |
| 5 | **Sinistralidade e ROI atípicos da Y** | Sinistralidade de **34,15%** e ROI assistencial de **192,80%**, muito abaixo dos patamares do setor (~80%+). | Apresentar uma margem que talvez não exista por descasamento de escopo entre receita e despesa. | Validar o escopo de receita e despesa (competência, itens, completude) antes de usar em precificação ou reajuste. |
| 6 | **Receita da Operadora X ausente** | Nenhuma linha de receita da X em 12 competências. | A carteira 4,8× maior que a Y fica sem avaliação de sustentabilidade financeira. | Solicitar a receita da X com prioridade; até lá, sinistralidade e ROI da X são **indisponíveis, nunca zero**. |
| 7 | **Coparticipação acima do valor bruto** | 22.345 eventos (0,53% na X; 0,11% na Y). Se truncados, a sinistralidade da Y vai de 34,15% para 34,24%. | Efeito imaterial, mas indica regra de lançamento não documentada. | Auditar a regra de coparticipação e publicar dicionário de dados com a definição oficial de despesa líquida. |

> Todos os números acima são recalculados e conferidos por `assert` na seção 8 do caderno 04. Se a base mudar, o caderno falha antes de apresentar um número desatualizado.

---

## 2. Esteira de dados

```
 data/Receita.csv ──► 01_auditoria_receita.ipynb ─┐
 data/Despesa.csv ──► 02_auditoria_despesa.ipynb ─┼─► 04_analise_consolidada_operadoras.ipynb ──► output/ (6 CSVs do contrato)
 data/Vidas.csv   ──► 03_auditoria_vidas.ipynb   ─┘                                              │
                                                                                                 │
 data/*.csv ──► scripts/gerar_tabelas_complementares_powerbi.py ──► output/ (2 CSVs complementares)
                                                                                                 │
                                                       ┌─────────────────────────────────────────┘
                                                       ▼
                         dashboard_projeto.pbip (Power BI)  ·  relatorio_executivo.html
```

| Etapa | Artefato | Papel |
|---|---|---|
| Auditoria | `01_auditoria_receita.ipynb` | Tipos, integridade e cobertura da Receita. Achado: **receita apenas da Operadora Y**. |
| Auditoria | `02_auditoria_despesa.ipynb` | Tipos, integridade e domínio de valores dos ~5 mi de eventos. Achado: **coparticipação > valor bruto**. |
| Auditoria | `03_auditoria_vidas.ipynb` | Tipos e integridade de Vidas. Achados: **perfil etário** das carteiras e **migração X → Y** em jan/2026. |
| Consolidação | `04_analise_consolidada_operadoras.ipynb` | Pipeline completo: indicadores, transferência de carteira, padronização etária, perfil de despesas, exportação blindada e verificação dos números citados. |
| Complemento BI | `scripts/gerar_tabelas_complementares_powerbi.py` | Gera as 2 tabelas de granularidade fina usadas pelas medidas de per capita padronizado e crescimento orgânico. |
| Consumo | `dashboard_projeto.pbip` · `relatorio_executivo.html` | Dashboard Power BI (4 páginas) e relatório executivo autocontido. |

Os cadernos 01 a 03 **não gravam dados**: documentam e testam as fontes. Apenas o caderno 04 e o script escrevem em `output/`.

**Contrato de dados com o Power BI.** Nomes de arquivo e colunas em `output/` são fixos (`SCHEMA_POWERBI`, seção 0 do caderno 04). Antes de sobrescrever, o caderno 04 compara colunas, tipos, linhas e chaves com a versão já publicada em `output/` e interrompe a execução se houver divergência.

---

## 3. Dicionário sumário — `output/`

| Arquivo | Granularidade | Colunas principais | Origem |
|---|---|---|---|
| `indicadores_mensais.csv` | Operadora × competência (24 linhas) | `despesa_bruta`, `coparticipacao`, `despesa_liquida`, `vidas`, `receita`, `sinistralidade_pct`, `roi_pct`, `custo_per_capita_mensal` | Caderno 04 |
| `indicadores_periodo.csv` | Operadora (2 linhas) | `receita_total`, `despesa_liquida_total`, `media_vidas`, `sinistralidade_pct`, `roi_pct`, `custo_per_capita`, `status_receita` | Caderno 04 |
| `perfil_carteira_faixa_etaria.csv` | Operadora × faixa etária (20) | `media_mensal_vidas`, `participacao_pct` | Caderno 04 |
| `perfil_despesas_faixa_etaria.csv` | Operadora × faixa etária (20) | `despesa_bruta_periodo`, `despesa_bruta_por_vida`, `participacao_vidas_pct`, `participacao_despesa_pct` | Caderno 04 |
| `perfil_despesas_classificacao.csv` | Operadora × classificação (34) | `despesa_bruta`, `participacao_pct` | Caderno 04 |
| `qualidade_dados_financeiros.csv` | Operadora (2) | `ocorrencias` (copart > bruto), `saldo_estimado_nas_ocorrencias`, `percentual_ocorrencias`, totais bruto/copart/líquido | Caderno 04 |
| `despesa_vidas_faixa_mensal.csv` | Operadora × competência × faixa (240) | `despesa_bruta`, `despesa_liquida`, `vidas` | Script complementar |
| `migracao_planos_mensal.csv` | Plano migrado × competência (24) | `Plano`, `papel_migracao`, `mes_migracao`, `vidas`, `despesa_liquida` | Script complementar |

**Convenções:** `data_ref` no formato `AAAA-MM-DD`; valores em R$; `*_pct` em pontos percentuais (0–100); despesa líquida = `valor_bruto − valor_coparticipacao`; indicadores do período por **razão de totais**; receita ausente = vazio (`NaN`), nunca zero. CSVs em UTF-8 com BOM.

---

## 4. Instalação e reprodução

Pré-requisitos: **Python 3.11+** (testado em 3.14) e as fontes `Receita.csv`, `Vidas.csv` e `Despesa.csv` em `data/`.

> `data/Despesa.csv` (≈ 950 MB) excede o limite do GitHub e está no `.gitignore`. Copie o arquivo original do desafio para `data/` antes de executar.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

Execução da esteira (a partir da raiz do projeto):

```bash
# Cadernos em ordem (ou abrir no Jupyter e usar "Restart & Run All")
jupyter nbconvert --to notebook --execute --inplace 01_auditoria_receita.ipynb
jupyter nbconvert --to notebook --execute --inplace 02_auditoria_despesa.ipynb
jupyter nbconvert --to notebook --execute --inplace 03_auditoria_vidas.ipynb
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 04_analise_consolidada_operadoras.ipynb

# Tabelas complementares do Power BI
python scripts/gerar_tabelas_complementares_powerbi.py
```

Todos os caminhos são relativos à raiz do projeto (os cadernos localizam a pasta `data/` automaticamente). O caderno 04 carrega ~5 milhões de eventos: reserve cerca de 4 GB de RAM.

---

## 5. Guia de visualização para avaliadores

### Relatório executivo (sem instalação)

Abra `relatorio_executivo.html` em qualquer navegador. O arquivo é autocontido, com os dados embutidos.

### Dashboard Power BI

Requer **Power BI Desktop** (Windows).

- **Projeto PBIP (versionado):** abra `dashboard_projeto.pbip`. As pastas `dashboard_projeto.Report/` e `dashboard_projeto.SemanticModel/` contêm o relatório e o modelo em texto e devem permanecer juntas ao `.pbip`.
- **Arquivo PBIX:** se recebido separadamente (não é versionado no Git), basta abrir `dashboard.pbix`.

**Ajuste do caminho dos dados.** O modelo lê os CSVs de `output/` pelo parâmetro `PastaOutput`, hoje apontando para a máquina de origem (`C:\Users\adrielle\Git\teste-pasa\output\`). Em outra máquina:

1. **Página Inicial → Transformar dados → Editar parâmetros**.
2. Informe o caminho absoluto da pasta `output\` desta cópia, **terminando em `\`**.
3. Clique em **Aplicar alterações** / **Atualizar**.

Páginas do dashboard: **Visão Executiva**, **Despesas e Indicadores**, **Perfil da Carteira** e **Qualidade e limitações**.

### Cadernos

Os cadernos são entregues **já executados**: podem ser lidos diretamente no GitHub, VS Code ou Jupyter, sem rodar nada.

---

## 6. Estrutura do repositório

```
teste-pasa/
├── 01_auditoria_receita.ipynb
├── 02_auditoria_despesa.ipynb
├── 03_auditoria_vidas.ipynb
├── 04_analise_consolidada_operadoras.ipynb
├── data/                              # fontes brutas (Despesa.csv fora do Git)
├── output/                            # 8 CSVs consumidos pelo Power BI
├── scripts/gerar_tabelas_complementares_powerbi.py
├── dashboard_projeto.pbip             # projeto Power BI (PBIP)
├── dashboard_projeto.Report/
├── dashboard_projeto.SemanticModel/
├── relatorio_executivo.html
├── logo-pasa.png
├── requirements.txt
└── README.md
```

## 7. Limitações

1. **Despesa líquida** é uma estimativa (`bruto − coparticipação`), sem dicionário oficial; a sensibilidade mostra efeito imaterial.
2. **Receita da X** está ausente; sinistralidade e ROI da X não são calculáveis.
3. **Escopo da receita da Y** precisa ser validado: a sinistralidade de 34% é atípica para o setor.
4. **Transferência de carteira** é inferida dos dados (data, porte, UF e perfil etário), sem documento contratual.
5. **Vidas** representam exposição mensal, não pessoas únicas; as análises são descritivas (associação ≠ causalidade).
