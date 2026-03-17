"""
1_Analise_Exploratoria.py
=========================
Página de análise exploratória interativa dos dados.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_data, INDICADORES, INDICADORES_DESC, PEDRAS_CORES
from utils.styles import inject_css, page_header, section_title, PLOTLY_LAYOUT, PLOTLY_COLORS

st.set_page_config(page_title="Análise Exploratória", layout="wide")
inject_css()

page_header("Análise Exploratória", "Explore os indicadores educacionais com filtros interativos e visualizações comparativas.")

df = load_data()
if df.empty:
    st.stop()

# =============================================================================
# SIDEBAR FILTROS
# =============================================================================
with st.sidebar:
    st.markdown("### Filtros")
    ano_sel = st.selectbox("Ano", ['Todos'] + sorted(df['Ano'].unique().tolist()))
    if ano_sel != 'Todos':
        df = df[df['Ano'] == int(ano_sel)]
    
    indicador_sel = st.selectbox("Indicador para análise", INDICADORES,
                                  format_func=lambda x: f"{x} - {INDICADORES_DESC.get(x, x)}")

# =============================================================================
# SECAO 1: DISTRIBUICAO DO INDICADOR SELECIONADO
# =============================================================================
section_title(f"Distribuição de {indicador_sel} ({INDICADORES_DESC.get(indicador_sel, '')})")

col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(
        df.dropna(subset=[indicador_sel]),
        x=indicador_sel,
        color='Ano' if ano_sel == 'Todos' else None,
        nbins=30,
        color_discrete_sequence=PLOTLY_COLORS,
        barmode='overlay',
        opacity=0.7,
    )
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=f'Histograma de {indicador_sel}', font=dict(size=16)))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.box(
        df.dropna(subset=[indicador_sel]),
        x='Pedra' if 'Pedra' in df.columns else 'Ano',
        y=indicador_sel,
        color='Pedra' if 'Pedra' in df.columns else 'Ano',
        color_discrete_map=PEDRAS_CORES,
    )
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=f'{indicador_sel} por Pedra', font=dict(size=16)))
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# SECAO 2: CORRELACOES
# =============================================================================
section_title("Matriz de Correlação entre Indicadores")

cols_corr = [c for c in INDICADORES + ['INDE'] if c in df.columns]
corr = df[cols_corr].corr()

fig = px.imshow(
    corr, text_auto='.2f',
    color_continuous_scale='Purples',
    aspect='auto',
    labels=dict(color='Correlação'),
)
fig.update_layout(**PLOTLY_LAYOUT, title=dict(text='Correlação entre Indicadores e INDE', font=dict(size=16)),
                  width=700, height=600)
st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# SECAO 3: SCATTER PLOT INTERATIVO
# =============================================================================
section_title("Análise Bivariada")

col1, col2, col3 = st.columns(3)
with col1:
    x_var = st.selectbox("Eixo X", INDICADORES + ['INDE'], index=0)
with col2:
    y_var = st.selectbox("Eixo Y", INDICADORES + ['INDE'], index=1)
with col3:
    color_var = st.selectbox("Cor", ['Pedra', 'Ano', 'Genero', 'Risco_Defasagem'])

df_scatter = df.dropna(subset=[x_var, y_var])

fig = px.scatter(
    df_scatter, x=x_var, y=y_var,
    color=color_var,
    color_discrete_map=PEDRAS_CORES if color_var == 'Pedra' else None,
    opacity=0.5,
    hover_data=['RA', 'Ano', 'Fase', 'INDE'],
)
fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=f'{x_var} vs {y_var}', font=dict(size=16)))
st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# SECAO 4: DEFASAGEM
# =============================================================================
section_title("Análise de Defasagem")

col1, col2 = st.columns(2)

with col1:
    defas_counts = df.groupby(['Ano', 'Risco_Defasagem']).size().reset_index(name='N')
    defas_counts['Status'] = defas_counts['Risco_Defasagem'].map({0: 'Sem Risco', 1: 'Em Risco'})
    fig = px.bar(
        defas_counts, x='Ano', y='N', color='Status',
        barmode='group',
        color_discrete_map={'Sem Risco': '#34D399', 'Em Risco': '#F87171'},
    )
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text='Risco de Defasagem por Ano', font=dict(size=16)))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(
        df.dropna(subset=['Defasagem']),
        x='Defasagem',
        color='Ano' if ano_sel == 'Todos' else None,
        nbins=15,
        barmode='overlay',
        opacity=0.7,
        color_discrete_sequence=PLOTLY_COLORS,
    )
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text='Distribuição da Defasagem', font=dict(size=16)))
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# SECAO 5: ESTATISTICAS DESCRITIVAS
# =============================================================================
section_title("Estatísticas Descritivas")

stats_cols = [c for c in INDICADORES + ['INDE', 'Defasagem'] if c in df.columns]
st.dataframe(
    df[stats_cols].describe().round(3).T,
    use_container_width=True,
)
