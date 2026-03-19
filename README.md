# Datathon Fase 5 - Passos Mágicos

**🌐 App ao vivo (Streamlit):** [https://datathon-5-ajttl.streamlit.app/](https://datathon-5-ajttl.streamlit.app/)

Análise de dados educacionais e modelo preditivo de risco de defasagem para a Associação Passos Mágicos.

## Sobre o Projeto

A **Associação Passos Mágicos** atua há 32 anos transformando a vida de crianças e jovens de baixa renda por meio da educação. Este projeto utiliza dados do PEDE (Pesquisa Extensiva do Desenvolvimento Educacional) de 2022, 2023 e 2024 para:

1. Responder **11 perguntas analíticas** sobre o desempenho dos alunos
2. Construir um **modelo preditivo de risco de defasagem**
3. Disponibilizar os resultados em uma **aplicação Streamlit interativa**

## Estrutura do Projeto

```
Tech Challenge 5/
├── Data/                              # Dados brutos (não modificar)
│   ├── BASE DE DADOS PEDE 2024 - DATATHON.xlsx
│   ├── Dicionário Dados Datathon.pdf
│   └── ...
├── data_processed/                    # Dados processados pelo ETL
│   ├── df_unificado.parquet
│   ├── df_unificado.csv
│   └── df_20XX.parquet
├── notebooks/                         # Scripts de análise
│   ├── 01_eda_limpeza.py             # ETL e limpeza de dados
│   ├── 02_analise_perguntas.py       # Respostas às 11 perguntas
│   └── 03_modelo_preditivo.py        # Modelo preditivo de risco
├── app/                               # Aplicação Streamlit
│   ├── 1_Visão_Geral.py              # Página principal
│   ├── pages/
│   │   ├── 1_Análise_Exploratória.py
│   │   ├── 2_Storytelling.py
│   │   └── 3_Predição_Risco.py
│   └── utils/
│       └── data_loader.py            # Utilitários de carregamento
├── models/                            # Modelo treinado
│   ├── modelo_risco_defasagem.joblib
│   ├── modelo_metadata.json
│   └── comparacao_modelos.csv
├── plots/                             # Gráficos gerados
├── requirements.txt
└── README.md
```

## Sobre a Estrutura

- **data_processed/**: Contém a base em `.parquet` após o tratamento (ETL), pronta para leitura veloz pela aplicação.
- **notebooks/**: Armazena o racional passo a passo do projeto. Dividido no ETL de limpeza e padronização (`01_eda_limpeza.py`), na carga de análises interativas que respondem às 11 perguntas de negócio (`02_analise_perguntas.py`), e na construção teórica do estimador (`03_modelo_preditivo.py`).
- **app/**: Abrigação das páginas que compõem a aplicação front-end Streamlit, orquestradas pelo `1_Visão_Geral.py`.
- **models/** e **plots/**: Artefatos congelados (como o `.joblib` do modelo) e gráficos estáticos gerados na EDA.

## Modelo Preditivo

### Objetivo
Prever o risco de defasagem de alunos com base nos indicadores educacionais.

### Metodologia
- **Variável-alvo:** Risco de Defasagem (Defasagem < 0, ou seja, aluno abaixo do nível ideal)
- **Features:** IDA, IEG, IAA, IPS, IPP, IPV, Notas (Mat, Por), Fase, Anos no Programa, Instituição, Gênero (13 features)
- **Separação:** Temporal - treino com 2022+2023, teste com 2024
- **Modelos avaliados:** Regressão Logística, Random Forest, Gradient Boosting
- **Nota:** IAN e INDE foram excluídos das features para evitar data leakage

### Resultados

| Modelo              | CV AUC | Accuracy | Precision | Recall | F1    | ROC-AUC |
|---------------------|--------|----------|-----------|--------|-------|---------|
| Regressão Logística | 0.668  | 0.602    | 0.554     | 0.708  | 0.622 | 0.617   |
| **Random Forest**   | 0.735  | 0.612    | 0.555     | 0.811  | 0.659 | 0.677   |
| Gradient Boosting   | ~0.73  | ~0.61    | ~0.55     | ~0.80  | ~0.65 | ~0.67   |

**Modelo selecionado:** Random Forest (F1=0.659, AUC=0.677, Recall=0.811)

### Feature Importance (Top 5)
1. IPV (Ponto de Virada): maior importância
2. IDA (Aprendizagem)
3. IEG (Engajamento)
4. Fase
5. Anos no Programa

## Principais Insights

1. **Defasagem em queda:** De 69.9% (2022) para 46.2% (2024)
2. **IDA e IPV são indicadores-chave:** para prever risco sem data leakage
3. **Engajamento importa:** IEG tem correlação de 0.539 com IDA
4. **Autoavaliação enviesada:** Alunos Quartzo superestimam seu desempenho em 2.29 pontos
5. **Programa funciona:** Proporção de alunos Topázio cresceu de 15.1% para 30.9%
6. **Escola pública:** Menor IDA mas maior Engajamento

## Autor

Arnaldo Janssen Tavares Toledo Laudares

## Licença

Este projeto foi desenvolvido para fins acadêmicos.
