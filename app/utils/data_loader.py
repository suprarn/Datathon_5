"""
data_loader.py
==============
Funções de carregamento e cache de dados para o app Streamlit.
"""

import pandas as pd
import numpy as np
import streamlit as st
import joblib
import json
import os

# Caminhos relativos à raiz do projeto
# __file__ = app/utils/data_loader.py → dirname → app/utils → dirname → app → dirname → raiz do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data_processed')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
PLOT_DIR = os.path.join(BASE_DIR, 'plots')
RAW_DATA_DIR = os.path.join(BASE_DIR, 'Data')
EXCEL_PATH = os.path.join(RAW_DATA_DIR, 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx')


@st.cache_data
def load_data():
    """Carrega o dataframe unificado processado."""
    parquet_path = os.path.join(DATA_DIR, 'df_unificado.parquet')
    if os.path.exists(parquet_path):
        return pd.read_parquet(parquet_path)
    else:
        st.error("Arquivo de dados processados não encontrado. Execute o notebook 01_eda_limpeza.py primeiro.")
        return pd.DataFrame()


@st.cache_data
def load_data_by_year(ano):
    """Carrega dados de um ano específico."""
    path = os.path.join(DATA_DIR, f'df_{ano}.parquet')
    if os.path.exists(path):
        return pd.read_parquet(path)
    else:
        df = load_data()
        return df[df['Ano'] == ano]


@st.cache_resource
def load_modelo():
    """Carrega o pipeline do modelo preditivo."""
    model_path = os.path.join(MODEL_DIR, 'modelo_risco_defasagem.joblib')
    if os.path.exists(model_path):
        return joblib.load(model_path)
    else:
        st.error("Modelo não encontrado. Execute o notebook 03_modelo_preditivo.py primeiro.")
        return None


@st.cache_data
def load_modelo_metadata():
    """Carrega metadados do modelo."""
    meta_path = os.path.join(MODEL_DIR, 'modelo_metadata.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


@st.cache_data
def load_feature_importances():
    """Carrega importâncias das features."""
    path = os.path.join(MODEL_DIR, 'feature_importances.csv')
    if os.path.exists(path):
        return pd.read_csv(path, index_col=0, header=None, names=['Importancia'])
    return pd.DataFrame()


def get_plot_path(filename):
    """Retorna caminho completo de um gráfico."""
    return os.path.join(PLOT_DIR, filename)


# Constantes do projeto
INDICADORES = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV']

INDICADORES_DESC = {
    'IAN': 'Adequação ao Nível',
    'IDA': 'Indicador de Aprendizagem',
    'IEG': 'Indicador de Engajamento',
    'IAA': 'Autoavaliação',
    'IPS': 'Indicador Psicossocial',
    'IPP': 'Indicador Psicopedagógico',
    'IPV': 'Ponto de Virada',
    'INDE': 'Índice de Desenvolvimento Educacional',
}

PEDRAS = ['Quartzo', 'Ágata', 'Ametista', 'Topázio']
PEDRAS_CORES = {'Quartzo': '#e74c3c', 'Ágata': '#f39c12', 'Ametista': '#3498db', 'Topázio': '#2ecc71'}
PEDRAS_FAIXAS = {
    'Quartzo': '2,405 a 5,506',
    'Ágata': '5,506 a 6,868',
    'Ametista': '6,868 a 8,230',
    'Topázio': '8,230 a 9,294',
}

FASES = ['ALFA', 'FASE 1', 'FASE 2', 'FASE 3', 'FASE 4', 'FASE 5', 'FASE 6', 'FASE 7', 'FASE 8']
