"""
1_Visão_Geral.py
======
App Streamlit principal — Datathon Fase 5: Passos Mágicos.
Página inicial com visão geral do projeto e métricas resumidas.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Adicionar diretorio raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.data_loader import load_data, INDICADORES_DESC, PEDRAS_CORES
from utils.styles import inject_css, section_title, PLOTLY_LAYOUT, PLOTLY_COLORS

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Passos Mágicos — Datathon",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# Extra CSS for the hero on this page only
st.markdown("""
<style>
    /* Fix sidebar nav: rename "app" to "Visão Geral" robustly */
    [data-testid="stSidebarNav"] li:first-child a > span {
        display: none !important;
    }
    [data-testid="stSidebarNav"] li:first-child a::after {
        content: "Visão Geral";
        font-size: 0.875rem;
        color: inherit;
        visibility: visible;
        margin-left: 0.2rem;
    }

    /* Hero container */
    .hero-container {
        background: linear-gradient(135deg, #1E1B4B 0%, #312E81 40%, #4C1D95 100%);
        padding: 3rem 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(167,139,250,0.15);
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        opacity: 0.5;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        color: #FFFFFF !important;
        margin: 0;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 15px rgba(0,0,0,0.3);
        position: relative;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #D1D5DB !important;
        margin-top: 0.6rem;
        font-weight: 400;
        position: relative;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(167,139,250,0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(167,139,250,0.25);
        padding: 0.35rem 1.2rem;
        border-radius: 50px;
        color: #E0D4FC !important;
        font-size: 0.75rem;
        font-weight: 500;
        margin-top: 1rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        position: relative;
    }

    /* Metric cards for this page */
    .metric-card {
        background: #1E2030;
        border: 1px solid rgba(102,126,234,0.2);
        padding: 1.3rem 1rem;
        border-radius: 14px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(167,139,250,0.5);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #A78BFA;
        line-height: 1.1;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #D1D5DB !important;
        text-transform: uppercase;
        letter-spacing: 0.7px;
        margin-top: 0.4rem;
        font-weight: 500;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(0,0,0,0.03);
        padding: 4px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 24px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.85rem;
        color: #374151 !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4C1D95, #6C63FF) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CABEÇALHO HERO
# =============================================================================
st.markdown("""
<div class="hero-container">
    <p class="hero-title">Passos Mágicos</p>
    <p class="hero-subtitle">Análise de dados educacionais e modelo preditivo de risco de defasagem escolar</p>
    <span class="hero-badge">Datathon Fase 5 &mdash; POSTECH DTAT</span>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# CARREGAR DADOS
# =============================================================================
df = load_data()

if df.empty:
    st.stop()

# =============================================================================
# SIDEBAR: FILTROS
# =============================================================================
with st.sidebar:
    st.markdown("### Filtros")
    
    anos_disponiveis = sorted(df['Ano'].unique())
    anos_selecionados = st.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)
    
    fases_disponiveis = sorted(df['Fase'].dropna().unique())
    fases_selecionadas = st.multiselect("Fase", fases_disponiveis, default=[])
    
    pedras_disponiveis = ['Quartzo', 'Ágata', 'Ametista', 'Topázio']
    pedras_selecionadas = st.multiselect("Pedra", pedras_disponiveis, default=[])
    
    generos_disponiveis = sorted(df['Genero'].dropna().unique())
    generos_selecionados = st.multiselect("Gênero", generos_disponiveis, default=[])
    
    st.markdown("""
    <div style="font-size: 0.72rem; color: #9CA3AF; text-align: center; padding: 1rem 0; border-top: 1px solid rgba(255,255,255,0.06); margin-top: 2rem;">
        Arnaldo Janssen T T L<br>
        POSTECH DTAT &mdash; 2026
    </div>
    """, unsafe_allow_html=True)

# Aplicar filtros
df_filtrado = df[df['Ano'].isin(anos_selecionados)] if anos_selecionados else df
if fases_selecionadas:
    df_filtrado = df_filtrado[df_filtrado['Fase'].isin(fases_selecionadas)]
if pedras_selecionadas:
    df_filtrado = df_filtrado[df_filtrado['Pedra'].isin(pedras_selecionadas)]
if generos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Genero'].isin(generos_selecionados)]

# =============================================================================
# MÉTRICAS RESUMIDAS
# =============================================================================
inde_medio = df_filtrado['INDE'].mean()
risco_pct = df_filtrado['Risco_Defasagem'].mean() * 100
topazio_pct = (df_filtrado['Pedra'] == 'Topázio').sum() / max(len(df_filtrado), 1) * 100

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(df_filtrado):,}</div>
        <div class="metric-label">Total de Alunos</div>
    </div>""", unsafe_allow_html=True)

with c2:
    val = f"{inde_medio:.2f}" if not np.isnan(inde_medio) else "N/A"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{val}</div>
        <div class="metric-label">INDE Médio</div>
    </div>""", unsafe_allow_html=True)

with c3:
    val = f"{risco_pct:.1f}%" if not np.isnan(risco_pct) else "N/A"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{val}</div>
        <div class="metric-label">Risco de Defasagem Escolar</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{topazio_pct:.1f}%</div>
        <div class="metric-label">Classificação Topázio</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =============================================================================
# GLOSSÁRIO DE SIGLAS
# =============================================================================
with st.expander("Glossário de Siglas e Indicadores", expanded=False):
    st.markdown("""
    <table class="glossary-table">
        <thead>
            <tr><th>Sigla</th><th>Nome</th><th>O que mede</th></tr>
        </thead>
        <tbody>
            <tr><td class="sigla">IAN</td><td>Adequação ao Nível</td><td>Se o aluno está no nível escolar adequado para sua idade</td></tr>
            <tr><td class="sigla">IDA</td><td>Indicador de Aprendizagem</td><td>Desempenho acadêmico real baseado em avaliações e notas</td></tr>
            <tr><td class="sigla">IEG</td><td>Indicador de Engajamento</td><td>Nível de participação, frequência e interesse nas atividades</td></tr>
            <tr><td class="sigla">IAA</td><td>Autoavaliação</td><td>A percepção que o aluno tem sobre seu próprio desempenho</td></tr>
            <tr><td class="sigla">IPS</td><td>Indicador Psicossocial</td><td>Bem-estar emocional, relações sociais e suporte familiar</td></tr>
            <tr><td class="sigla">IPP</td><td>Indicador Psicopedagógico</td><td>Acompanhamento e suporte pedagógico recebido</td></tr>
            <tr><td class="sigla">IPV</td><td>Ponto de Virada</td><td>Momento de transformação na trajetória educacional do aluno</td></tr>
            <tr><td class="sigla">INDE</td><td>Índice de Desenvolvimento Educacional</td><td>Nota global calculada a partir dos 7 indicadores acima</td></tr>
            <tr><td class="sigla">Pedra</td><td>Classificação por Pedra</td><td>Faixa do INDE: Quartzo (menor) &rarr; Ágata &rarr; Ametista &rarr; Topázio (maior)</td></tr>
            <tr><td class="sigla">Defasagem</td><td>Defasagem Escolar</td><td>Diferença entre a fase ideal para a idade e a fase real do aluno</td></tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)

# =============================================================================
# VISÃO GERAL EM TABS
# =============================================================================
tab1, tab2, tab3 = st.tabs(["Distribuição de Pedras", "INDE por Ano", "Radar de Indicadores"])


with tab1:
    pedra_counts = df_filtrado.groupby(['Ano', 'Pedra']).size().reset_index(name='Contagem')
    fig = px.bar(
        pedra_counts, x='Ano', y='Contagem', color='Pedra',
        color_discrete_map=PEDRAS_CORES,
        barmode='group',
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text='Distribuição de Pedras por Ano', font=dict(size=18)),
        xaxis_title='Ano', yaxis_title='Quantidade de Alunos',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = px.box(
        df_filtrado.dropna(subset=['INDE']), x='Ano', y='INDE',
        color='Ano',
        color_discrete_sequence=PLOTLY_COLORS,
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text='Distribuição do INDE por Ano', font=dict(size=18)),
        xaxis_title='Ano', yaxis_title='INDE',
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    indicadores = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV']
    fig = go.Figure()
    
    cores_radar = ['#6C63FF', '#F093FB', '#38BDF8']
    for i, ano in enumerate(sorted(df_filtrado['Ano'].unique())):
        df_ano = df_filtrado[df_filtrado['Ano'] == ano]
        medias = [df_ano[ind].mean() for ind in indicadores]
        fig.add_trace(go.Scatterpolar(
            r=medias + [medias[0]],
            theta=[INDICADORES_DESC.get(i, i) for i in indicadores] + [INDICADORES_DESC.get(indicadores[0], indicadores[0])],
            fill='toself',
            name=str(ano),
            opacity=0.65,
            line=dict(width=2, color=cores_radar[i % len(cores_radar)]),
        ))
    
    fig.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], gridcolor='rgba(255,255,255,0.1)'),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            bgcolor='rgba(0,0,0,0)',
        ),
        showlegend=True,
        title=dict(text='Indicadores Médios por Ano', font=dict(size=18)),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# TABELA DE DADOS
# =============================================================================
with st.expander("Ver dados filtrados"):
    colunas_exibir = ['RA', 'Ano', 'Fase', 'INDE', 'Pedra', 'IAN', 'IDA', 'IEG',
                      'IAA', 'IPS', 'IPP', 'IPV', 'Defasagem', 'Genero']
    colunas_existentes = [c for c in colunas_exibir if c in df_filtrado.columns]
    st.dataframe(df_filtrado[colunas_existentes], use_container_width=True, height=400)
