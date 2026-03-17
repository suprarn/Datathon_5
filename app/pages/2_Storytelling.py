"""
2_Storytelling.py
=================
Página de storytelling com respostas às 10 perguntas analíticas do Datathon.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import load_data, INDICADORES_DESC, PEDRAS_CORES
from utils.styles import (inject_css, page_header, section_title, insight_card,
                           question_card, PLOTLY_LAYOUT, PLOTLY_COLORS)

st.set_page_config(page_title="Storytelling", layout="wide")
inject_css()

page_header("Storytelling",
            "Respostas às perguntas do Datathon com visualizações interativas e insights baseados em dados.")

df = load_data()
if df.empty:
    st.stop()

# =============================================================================
# PERGUNTA 1: Adequacao do nivel (IAN)
# =============================================================================
section_title("1. Adequação do Nível (IAN)")
question_card("Qual é o perfil geral de defasagem dos alunos e como ele evolui ao longo do ano?")

col1, col2 = st.columns(2)

with col1:
    risco_ano = df.groupby('Ano')['Risco_Defasagem'].mean() * 100
    fig = go.Figure()
    fig.add_trace(go.Bar(x=risco_ano.index.astype(str), y=risco_ano.values,
                         marker_color=['#F87171', '#FBBF24', '#34D399'],
                         text=[f'{v:.1f}%' for v in risco_ano.values],
                         textposition='outside',
                         textfont=dict(size=14, color='#E5E7EB')))
    fig.update_layout(**PLOTLY_LAYOUT,
                      title=dict(text='% Alunos com Defasagem por Ano', font=dict(size=16)),
                      xaxis_title='Ano', yaxis_title='% com Defasagem')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    ian_ano = df.groupby('Ano')['IAN'].mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ian_ano.index, y=ian_ano.values,
                             mode='lines+markers+text',
                             text=[f'{v:.2f}' for v in ian_ano.values],
                             textposition='top center',
                             textfont=dict(size=13, color='#E5E7EB'),
                             line=dict(width=3, color='#6C63FF'),
                             marker=dict(size=10, color='#A78BFA')))
    fig.update_layout(**PLOTLY_LAYOUT,
                      title=dict(text='IAN Médio por Ano', font=dict(size=16)),
                      xaxis_title='Ano', yaxis_title='IAN')
    st.plotly_chart(fig, use_container_width=True)

insight_card("<strong>Insight:</strong> O percentual de alunos abaixo do nível ideal caiu de 69.9% (2022) para 46.2% (2024), enquanto o IAN médio subiu de 6.42 para 7.68. Isso indica uma melhoria significativa de quase 24 pontos percentuais em 3 anos.")

st.divider()

# =============================================================================
# PERGUNTA 2: Desempenho academico (IDA)
# =============================================================================
section_title("2. Desempenho Acadêmico (IDA)")
question_card("O IDA está melhorando, estagnado ou caindo ao longo das fases e anos?")

ida_stats = df.groupby('Ano')['IDA'].agg(['mean', 'median', 'std']).reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(x=ida_stats['Ano'], y=ida_stats['mean'],
                         mode='lines+markers', name='Média',
                         line=dict(width=3, color='#34D399'),
                         marker=dict(size=8)))
fig.add_trace(go.Scatter(x=ida_stats['Ano'], y=ida_stats['median'],
                         mode='lines+markers', name='Mediana',
                         line=dict(width=3, color='#38BDF8', dash='dash'),
                         marker=dict(size=8)))
fig.update_layout(**PLOTLY_LAYOUT,
                  title=dict(text='Evolução do IDA', font=dict(size=16)),
                  xaxis_title='Ano', yaxis_title='IDA')
st.plotly_chart(fig, use_container_width=True)

insight_card("<strong>Insight:</strong> O IDA médio apresentou melhoria de 2022 (6.09) para 2023 (6.66) e uma leve redução em 2024 (6.35). A mediana segue padrão similar. O desempenho acadêmico mostrou tendência de melhora mas com variação no último ano.")

st.divider()

# =============================================================================
# PERGUNTA 3: Engajamento x Desempenho (IEG x IDA x IPV)
# =============================================================================
section_title("3. Engajamento x Desempenho (IEG x IDA x IPV)")
question_card("O grau de engajamento tem relação direta com desempenho e ponto de virada?")

df_valid = df.dropna(subset=['IEG', 'IDA', 'IPV'])
fig = px.scatter(df_valid, x='IEG', y='IDA', color='IPV',
                 color_continuous_scale='Viridis',
                 opacity=0.5,
                 hover_data=['RA', 'Ano'])
fig.update_layout(**PLOTLY_LAYOUT,
                  title=dict(text='IEG vs IDA, colorido por IPV', font=dict(size=16)))
st.plotly_chart(fig, use_container_width=True)

corr_3 = df[['IEG', 'IDA', 'IPV']].corr()
col1, col2, col3 = st.columns(3)
col1.metric("Corr IEG-IDA", f"{corr_3.loc['IEG','IDA']:.3f}")
col2.metric("Corr IEG-IPV", f"{corr_3.loc['IEG','IPV']:.3f}")
col3.metric("Corr IDA-IPV", f"{corr_3.loc['IDA','IPV']:.3f}")

insight_card("<strong>Insight:</strong> Existe uma correlação positiva moderada entre os três indicadores (IEG-IDA: 0.539, IEG-IPV: 0.558, IDA-IPV: 0.557). Alunos mais engajados tendem a ter melhor desempenho e maior probabilidade de atingir o ponto de virada.")

st.divider()

# =============================================================================
# PERGUNTA 4: Autoavaliacao (IAA x IDA)
# =============================================================================
section_title("4. Autoavaliação (IAA x IDA)")
question_card("As percepções dos alunos são coerentes com seu desempenho real?")

df_valid4 = df.dropna(subset=['IAA', 'IDA']).copy()
df_valid4['Gap'] = df_valid4['IAA'] - df_valid4['IDA']

col1, col2 = st.columns(2)

with col1:
    fig = px.scatter(df_valid4, x='IAA', y='IDA', color='Pedra',
                     color_discrete_map=PEDRAS_CORES, opacity=0.4)
    lim_min = min(df_valid4[['IAA','IDA']].min())
    lim_max = max(df_valid4[['IAA','IDA']].max())
    fig.add_shape(type='line', x0=lim_min, y0=lim_min, x1=lim_max, y1=lim_max,
                  line=dict(color='#F87171', dash='dash', width=2))
    fig.update_layout(**PLOTLY_LAYOUT,
                      title=dict(text='Autoavaliação (IAA) vs Desempenho Real (IDA)', font=dict(size=15)))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    gap_pedra = df_valid4.groupby('Pedra')['Gap'].mean().reset_index()
    fig = px.bar(gap_pedra, x='Pedra', y='Gap', color='Pedra',
                 color_discrete_map=PEDRAS_CORES)
    fig.add_hline(y=0, line_dash='dash', line_color='#F87171', line_width=2)
    fig.update_layout(**PLOTLY_LAYOUT,
                      title=dict(text='Gap Médio (IAA - IDA) por Pedra', font=dict(size=15)))
    st.plotly_chart(fig, use_container_width=True)

insight_card("<strong>Insight:</strong> Todos os grupos superestimam seu desempenho (gap positivo), mas alunos Quartzo têm o maior gap (2.29) enquanto Topázio têm o menor (0.84). Alunos com menor desempenho têm menor consciência de suas dificuldades.")

st.divider()

# =============================================================================
# PERGUNTA 5: Padroes psicossociais (IPS)
# =============================================================================
section_title("5. Padrões Psicossociais (IPS)")
question_card("Há padrões psicossociais que antecedem quedas de desempenho?")

resultados_delta = []
for ano_ant, ano_post in [(2022, 2023), (2023, 2024)]:
    df_ant = df[df['Ano'] == ano_ant][['RA', 'IDA', 'IPS']].rename(
        columns={'IDA': 'IDA_ant', 'IPS': 'IPS_ant'})
    df_post_yr = df[df['Ano'] == ano_post][['RA', 'IDA']].rename(columns={'IDA': 'IDA_post'})
    merged = df_ant.merge(df_post_yr, on='RA', how='inner').dropna()
    merged['Delta_IDA'] = merged['IDA_post'] - merged['IDA_ant']
    merged['Piorou'] = (merged['Delta_IDA'] < 0).map({True: 'Piorou', False: 'Melhorou'})
    resultados_delta.append(merged)

df_delta = pd.concat(resultados_delta, ignore_index=True)

fig = px.box(df_delta, x='Piorou', y='IPS_ant', color='Piorou',
             color_discrete_map={'Piorou': '#F87171', 'Melhorou': '#34D399'})
fig.update_layout(**PLOTLY_LAYOUT,
                  title=dict(text='IPS no ano anterior: Melhoraram vs Pioraram', font=dict(size=16)))
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
ips_piorou = df_delta.groupby('Piorou')['IPS_ant'].mean()
col1.metric("IPS médio - Melhoraram", f"{ips_piorou.get('Melhorou', 0):.3f}")
col2.metric("IPS médio - Pioraram", f"{ips_piorou.get('Piorou', 0):.3f}")

insight_card("<strong>Insight:</strong> Alunos que pioraram o IDA tinham IPS médio anterior ligeiramente menor (5.87 vs 6.06). Padrões psicossociais fragilizados podem ser um indicador precoce de queda no desempenho.")

st.divider()

# =============================================================================
# PERGUNTA 6: Psicopedagogico (IPP x IAN)
# =============================================================================
section_title("6. Psicopedagógico (IPP x IAN)")
question_card("As avaliações psicopedagógicas confirmam ou contradizem a defasagem?")

df_valid6 = df.dropna(subset=['IPP', 'IAN'])
fig = px.scatter(df_valid6, x='IPP', y='IAN', color='Defasagem',
                 color_continuous_scale='RdYlGn_r', opacity=0.4)
fig.update_layout(**PLOTLY_LAYOUT,
                  title=dict(text='IPP vs IAN, colorido por Defasagem', font=dict(size=16)))
st.plotly_chart(fig, use_container_width=True)

corr_6 = df[['IPP', 'IAN', 'Defasagem']].corr()
st.markdown(f"""
- Correlação IPP-IAN: **{corr_6.loc['IPP','IAN']:.3f}** (fraca)
- Correlação IAN-Defasagem: **{corr_6.loc['IAN','Defasagem']:.3f}** (forte)
- Correlação IPP-Defasagem: **{corr_6.loc['IPP','Defasagem']:.3f}** (fraca)
""")

insight_card("<strong>Insight:</strong> A correlação entre IPP e IAN é fraca (0.12), sugerindo que a avaliação psicopedagógica captura dimensões diferentes da defasagem. O IAN tem forte correlação com a defasagem (0.86), confirmando-se como o indicador mais direto.")

st.divider()

# =============================================================================
# PERGUNTA 7: Ponto de virada (IPV)
# =============================================================================
section_title("7. Ponto de Virada (IPV)")
question_card("Quais comportamentos mais influenciam o IPV?")

df_ipv = df.dropna(subset=['IPV']).copy()
df_ipv['IPV_Nivel'] = pd.qcut(df_ipv['IPV'], q=3, labels=['Baixo', 'Médio', 'Alto'])

indicadores = ['IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IAN']
ipv_profile = df_ipv.groupby('IPV_Nivel')[indicadores].mean()

fig = go.Figure()
cores_radar = ['#F87171', '#FBBF24', '#34D399']
for i, nivel in enumerate(['Baixo', 'Médio', 'Alto']):
    valores = ipv_profile.loc[nivel].values
    fig.add_trace(go.Scatterpolar(
        r=list(valores) + [valores[0]],
        theta=indicadores + [indicadores[0]],
        fill='toself', name=nivel, opacity=0.6,
        line=dict(color=cores_radar[i], width=2)))

fig.update_layout(
    **PLOTLY_LAYOUT,
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 10], gridcolor='rgba(255,255,255,0.1)'),
        angularaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        bgcolor='rgba(0,0,0,0)',
    ),
    title=dict(text='Perfil de Indicadores por Nível de IPV', font=dict(size=16)),
    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
)
st.plotly_chart(fig, use_container_width=True)

insight_card("<strong>Insight:</strong> Alunos com IPV alto se destacam em todos os indicadores, especialmente IDA (7.55 vs 5.08 no grupo baixo) e IEG (9.07 vs 7.23). O desempenho acadêmico e o engajamento são os maiores preditores do ponto de virada.")

st.divider()

# =============================================================================
# PERGUNTA 8: Multidimensionalidade (INDE)
# =============================================================================
section_title("8. Multidimensionalidade dos Indicadores (INDE)")
question_card("Quais combinações de indicadores elevam mais a nota global (INDE)?")

corr_inde = df[indicadores + ['INDE']].corr()['INDE'].drop('INDE').sort_values(ascending=True)

fig = go.Figure()
fig.add_trace(go.Bar(x=corr_inde.values, y=corr_inde.index,
                     orientation='h',
                     marker_color=px.colors.sequential.Purples[2:2+len(corr_inde)],
                     text=[f'{v:.3f}' for v in corr_inde.values],
                     textposition='outside',
                     textfont=dict(color='#E5E7EB')))
fig.update_layout(**PLOTLY_LAYOUT,
                  title=dict(text='Correlação de cada Indicador com o INDE', font=dict(size=16)),
                  xaxis_title='Correlação', yaxis_title='Indicador')
st.plotly_chart(fig, use_container_width=True)

insight_card("<strong>Insight:</strong> IDA (0.785), IEG (0.745) e IPV (0.721) são os indicadores que mais elevam o INDE. O modelo linear com todos os indicadores explica 100% da variância (R2=1.0), confirmando que o INDE é uma combinação ponderada exata.")

st.divider()

# =============================================================================
# PERGUNTA 10: Efetividade do programa
# =============================================================================
section_title("10. Efetividade do Programa")
question_card("Os indicadores mostram melhora consistente ao longo das fases?")

col1, col2 = st.columns(2)

with col1:
    pedra_pct = pd.crosstab(df['Ano'], df['Pedra'], normalize='index') * 100
    fig = go.Figure()
    for pedra in ['Quartzo', 'Ágata', 'Ametista', 'Topázio']:
        if pedra in pedra_pct.columns:
            fig.add_trace(go.Bar(x=pedra_pct.index.astype(str), y=pedra_pct[pedra],
                                name=pedra, marker_color=PEDRAS_CORES.get(pedra)))
    fig.update_layout(**PLOTLY_LAYOUT, barmode='stack',
                      title=dict(text='Distribuição de Pedras por Ano (%)', font=dict(size=15)),
                      xaxis_title='Ano', yaxis_title='%')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    transicoes = []
    for ano_a, ano_b in [(2022, 2023), (2023, 2024)]:
        df_a = df[df['Ano'] == ano_a][['RA', 'Pedra_Num']].rename(columns={'Pedra_Num': 'Pedra_A'})
        df_b = df[df['Ano'] == ano_b][['RA', 'Pedra_Num']].rename(columns={'Pedra_Num': 'Pedra_B'})
        merged = df_a.merge(df_b, on='RA').dropna()
        merged['Trans'] = merged['Pedra_B'] - merged['Pedra_A']
        subiu = (merged['Trans'] > 0).mean() * 100
        manteve = (merged['Trans'] == 0).mean() * 100
        desceu = (merged['Trans'] < 0).mean() * 100
        transicoes.append({'Periodo': f'{ano_a}->{ano_b}', 'Subiram': subiu,
                          'Mantiveram': manteve, 'Desceram': desceu})
    
    df_trans = pd.DataFrame(transicoes)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_trans['Periodo'], y=df_trans['Subiram'],
                         name='Subiram', marker_color='#34D399'))
    fig.add_trace(go.Bar(x=df_trans['Periodo'], y=df_trans['Mantiveram'],
                         name='Mantiveram', marker_color='#FBBF24'))
    fig.add_trace(go.Bar(x=df_trans['Periodo'], y=df_trans['Desceram'],
                         name='Desceram', marker_color='#F87171'))
    fig.update_layout(**PLOTLY_LAYOUT, barmode='group',
                      title=dict(text='Transições de Pedra entre Anos (%)', font=dict(size=15)),
                      yaxis_title='%')
    st.plotly_chart(fig, use_container_width=True)

insight_card("<strong>Insight:</strong> A proporção de alunos Topázio cresceu de 15.1% (2022) para 30.9% (2024), enquanto Quartzo caiu de 15.3% para 10.6%. Nas transições individuais, ~24% dos alunos sobem de pedra a cada ano. Isso evidencia um impacto real e positivo do programa.")

st.divider()

# =============================================================================
# PERGUNTA 11: Insights criativos
# =============================================================================
section_title("11. Insights Criativos")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Gênero e Desempenho")
    genero_stats = df.groupby('Genero')[['INDE', 'IDA', 'IEG', 'IPV']].mean().reset_index()
    fig = px.bar(genero_stats, x='Genero', y=['INDE', 'IDA', 'IEG', 'IPV'],
                 barmode='group', color_discrete_sequence=PLOTLY_COLORS)
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text='Indicadores por Gênero', font=dict(size=15)))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("##### Tempo no Programa e INDE")
    anos_prog = df.groupby('Anos_No_Programa')['INDE'].mean().reset_index()
    fig = px.line(anos_prog, x='Anos_No_Programa', y='INDE',
                  markers=True, color_discrete_sequence=['#A78BFA'])
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text='INDE Médio vs Tempo no Programa', font=dict(size=15)))
    st.plotly_chart(fig, use_container_width=True)

# Tipo de instituicao
st.markdown("##### Instituição Pública vs Privada")
inst_stats = df.groupby('Instituicao_Publica')[['INDE', 'IDA', 'IEG']].mean()
inst_stats.index = ['Privada/Outra', 'Publica']

col1, col2, col3 = st.columns(3)
col1.metric("INDE Pública", f"{inst_stats.loc['Publica', 'INDE']:.2f}",
            delta=f"{inst_stats.loc['Publica', 'INDE'] - inst_stats.loc['Privada/Outra', 'INDE']:.2f}")
col2.metric("IDA Pública", f"{inst_stats.loc['Publica', 'IDA']:.2f}",
            delta=f"{inst_stats.loc['Publica', 'IDA'] - inst_stats.loc['Privada/Outra', 'IDA']:.2f}")
col3.metric("IEG Pública", f"{inst_stats.loc['Publica', 'IEG']:.2f}",
            delta=f"{inst_stats.loc['Publica', 'IEG'] - inst_stats.loc['Privada/Outra', 'IEG']:.2f}")

insight_card("<strong>Insight:</strong> Alunos de escolas públicas têm IDA menor (-0.73) mas IEG maior (+1.36), sugerindo que, apesar de dificuldades acadêmicas, o engajamento com o programa pode ser maior entre alunos de escola pública.")
