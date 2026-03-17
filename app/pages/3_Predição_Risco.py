"""
3_Predicao_Risco.py
===================
Página de predição de risco de defasagem com modelo ML.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import (load_modelo, load_modelo_metadata,
                                load_feature_importances, INDICADORES_DESC)
from utils.styles import inject_css, page_header, section_title, insight_card, PLOTLY_LAYOUT

st.set_page_config(page_title="Predição de Risco", layout="wide")
inject_css()

page_header("Predição de Risco de Defasagem",
            "Insira os indicadores de um aluno para calcular a probabilidade de risco usando nosso modelo Random Forest.")

# Carregar modelo e metadados
modelo = load_modelo()
metadata = load_modelo_metadata()
feat_imp = load_feature_importances()

if modelo is None:
    st.error("Modelo não carregado. Execute o notebook 03_modelo_preditivo.py primeiro.")
    st.stop()

# =============================================================================
# INFORMAÇÕES DO MODELO
# =============================================================================
with st.expander("Informações do Modelo", expanded=False):
    if metadata:
        col1, col2, col3, col4 = st.columns(4)
        metricas = metadata.get('metricas', {})
        col1.metric("Modelo", metadata.get('nome', 'N/A'))
        col2.metric("F1-Score", f"{metricas.get('f1', 0):.3f}")
        col3.metric("ROC-AUC", f"{metricas.get('roc_auc', 0):.3f}")
        col4.metric("Recall", f"{metricas.get('recall', 0):.3f}")
        
        st.markdown(f"""
        - **Dados de treino:** {metadata.get('treino_anos', [])} ({metadata.get('treino_n', 0)} amostras)
        - **Dados de teste:** {metadata.get('teste_ano', '')} ({metadata.get('teste_n', 0)} amostras)
        - **Features:** {', '.join(metadata.get('features', []))}
        """)

st.markdown("<br>", unsafe_allow_html=True)

# =============================================================================
# FORMULÁRIO DE ENTRADA
# =============================================================================
section_title("Dados do Aluno")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("##### Indicadores Acadêmicos")
    ida = st.slider("IDA (Aprendizagem)", 0.0, 10.0, 6.5, 0.1,
                    help="Indicador de Aprendizagem")
    nota_mat = st.slider("Nota Matemática", 0.0, 10.0, 6.0, 0.1)
    nota_por = st.slider("Nota Português", 0.0, 10.0, 6.0, 0.1)

with col2:
    st.markdown("##### Indicadores Comportamentais")
    ieg = st.slider("IEG (Engajamento)", 0.0, 10.0, 8.0, 0.1,
                    help="Indicador de Engajamento")
    iaa = st.slider("IAA (Autoavaliação)", 0.0, 10.0, 7.5, 0.1,
                    help="Indicador de Autoavaliação")
    ipv = st.slider("IPV (Ponto de Virada)", 0.0, 10.0, 7.0, 0.1,
                    help="Indicador de Ponto de Virada")

with col3:
    st.markdown("##### Psicossociais e Dados")
    ips = st.slider("IPS (Psicossocial)", 0.0, 10.0, 6.0, 0.1,
                    help="Indicador Psicossocial")
    ipp = st.slider("IPP (Psicopedagógico)", 0.0, 10.0, 7.0, 0.1,
                    help="Indicador Psicopedagógico")
    fase_num = st.selectbox("Fase", list(range(0, 9)),
                            format_func=lambda x: f"ALFA" if x == 0 else f"FASE {x}")
    anos_programa = st.number_input("Anos no Programa", 0, 15, 2)
    genero = st.radio("Gênero", ["Masculino", "Feminino"], horizontal=True)
    instituicao = st.radio("Tipo de Instituição", ["Pública", "Privada"], horizontal=True)
    num_avaliacoes = st.number_input("Número de Avaliações", 1, 10, 3)

# =============================================================================
# PREDIÇÃO
# =============================================================================
st.markdown("<br>", unsafe_allow_html=True)

if st.button("Calcular Risco de Defasagem", type="primary", use_container_width=True):
    # Montar dataframe de entrada
    features_ordem = metadata.get('features', [
        'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV',
        'Nota_Mat', 'Nota_Por', 'Fase_Num', 'Anos_No_Programa',
        'Instituicao_Publica', 'Genero_Num', 'Num_Avaliacoes'
    ])
    
    valores = {
        'IDA': ida, 'IEG': ieg, 'IAA': iaa,
        'IPS': ips, 'IPP': ipp, 'IPV': ipv,
        'Nota_Mat': nota_mat, 'Nota_Por': nota_por,
        'Fase_Num': fase_num,
        'Anos_No_Programa': anos_programa,
        'Instituicao_Publica': 1 if instituicao == 'Pública' else 0,
        'Genero_Num': 0 if genero == 'Masculino' else 1,
        'Num_Avaliacoes': num_avaliacoes,
    }
    
    X_input = pd.DataFrame([{f: valores.get(f, 0) for f in features_ordem}])
    
    try:
        probabilidade = modelo.predict_proba(X_input)[0][1]
        predicao = modelo.predict(X_input)[0]
        
        # Classificação visual
        if probabilidade < 0.3:
            risco_label = "BAIXO"
            risco_cor = "#34D399"
            risco_bg = "rgba(52,211,153,0.1)"
        elif probabilidade < 0.6:
            risco_label = "MÉDIO"
            risco_cor = "#FBBF24"
            risco_bg = "rgba(251,191,36,0.1)"
        else:
            risco_label = "ALTO"
            risco_cor = "#F87171"
            risco_bg = "rgba(248,113,113,0.1)"
        
        # Layout de resultado
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=probabilidade * 100,
                number={'suffix': '%', 'font': {'size': 48, 'color': '#1F2937'}},
                title={'text': 'Probabilidade de Risco', 'font': {'color': '#4B5563', 'size': 14}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': '#D1D5DB'},
                    'bar': {'color': risco_cor, 'thickness': 0.8},
                    'bgcolor': '#F3F4F6',
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 30], 'color': 'rgba(52,211,153,0.15)'},
                        {'range': [30, 60], 'color': 'rgba(251,191,36,0.15)'},
                        {'range': [60, 100], 'color': 'rgba(248,113,113,0.15)'},
                    ],
                    'threshold': {
                        'line': {'color': '#F87171', 'width': 3},
                        'thickness': 0.75, 'value': 60
                    }
                }
            ))
            fig.update_layout(height=350, **PLOTLY_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: {risco_bg}; border: 1px solid {risco_cor}33; border-radius: 14px; padding: 1.5rem; margin-top: 1rem;">
                <p style="font-size: 0.8rem; color: #6B7280; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin: 0;">Nível de Risco</p>
                <p style="font-size: 2.5rem; font-weight: 800; color: {risco_cor}; margin: 0.3rem 0; text-shadow: 0px 1px 2px rgba(0,0,0,0.1);">{risco_label}</p>
                <p style="font-size: 1.1rem; color: #1F2937; margin: 0;">Probabilidade: <strong style="color: #111827;">{probabilidade*100:.1f}%</strong></p>
                <p style="font-size: 0.95rem; color: #4B5563; font-weight: 500; margin-top: 0.5rem;">{'Em Risco de Defasagem' if predicao == 1 else 'Sem Risco de Defasagem'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if risco_label == "BAIXO":
                st.success("O aluno apresenta baixo risco de estar abaixo do nível ideal. Os indicadores estão em níveis adequados.")
            elif risco_label == "MÉDIO":
                st.warning("O aluno apresenta risco moderado de estar abaixo do nível ideal. Recomenda-se acompanhamento próximo, especialmente nos indicadores IPV e IDA.")
            else:
                st.error("O aluno apresenta alto risco de estar abaixo do nível ideal. Recomenda-se intervenção imediata com foco em engajamento e apoio psicopedagógico.")
    
    except Exception as e:
        st.error(f"Erro na predição: {str(e)}")

# =============================================================================
# IMPORTÂNCIA DAS FEATURES
# =============================================================================
st.markdown("<br>", unsafe_allow_html=True)
section_title("Importância das Features no Modelo")

if not feat_imp.empty:
    feat_imp_sorted = feat_imp.sort_values('Importancia', ascending=True)
    
    # Gradient colors for bars
    n = len(feat_imp_sorted)
    colors = [f'rgba(108,99,255,{0.3 + 0.7 * i/n})' for i in range(n)]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=feat_imp_sorted['Importancia'],
        y=feat_imp_sorted.index,
        orientation='h',
        marker_color=colors,
        text=[f'{v:.4f}' for v in feat_imp_sorted['Importancia']],
        textposition='outside',
        textfont=dict(color='#374151', size=11, weight='bold'),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text='Features mais importantes para a predição', font=dict(size=16)),
        xaxis_title='Importância',
        yaxis_title='Feature',
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)
    
    insight_card("<strong>IPV (Ponto de Virada)</strong> e <strong>IEG (Engajamento)</strong> são as features mais importantes, seguidas por Fase e IDA. IAN e INDE foram excluídos para evitar data leakage.")
