"""
02_analise_perguntas.py
=======================
Fase 2 do Datathon: Respostas às 11 perguntas analíticas do guia.
Gera visualizações e insights para o storytelling.

Autor: Equipe Datathon Fase 5
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data_processed')
PLOT_DIR = os.path.join(BASE_DIR, 'plots')
os.makedirs(PLOT_DIR, exist_ok=True)

plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
sns.set_theme(style='whitegrid', palette='viridis')

# Carregar dados
df = pd.read_parquet(os.path.join(DATA_DIR, 'df_unificado.parquet'))
print(f"Dados carregados: {df.shape}")

# =============================================================================
# PERGUNTA 1: Adequação do nível (IAN)
# Qual é o perfil geral de defasagem dos alunos e como evolui ao longo do ano?
# =============================================================================
print("\n" + "="*60)
print("PERGUNTA 1: Adequação do nível (IAN)")
print("="*60)

# Distribuição da defasagem por ano
fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
for i, ano in enumerate([2022, 2023, 2024]):
    df_ano = df[df['Ano'] == ano]
    defas_counts = df_ano['Defasagem'].value_counts().sort_index()
    axes[i].bar(defas_counts.index.astype(str), defas_counts.values, color=sns.color_palette('viridis', len(defas_counts)))
    axes[i].set_title(f'Defasagem em {ano}')
    axes[i].set_xlabel('Nível de Defasagem')
    axes[i].set_ylabel('Quantidade de Alunos' if i == 0 else '')
    # Anotar valores
    for j, (idx, val) in enumerate(zip(defas_counts.index, defas_counts.values)):
        axes[i].text(j, val + 2, str(val), ha='center', fontsize=9)
plt.suptitle('Pergunta 1: Distribuição da Defasagem por Ano', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'p1_defasagem_por_ano.png'), dpi=150, bbox_inches='tight')
plt.close()

# IAN médio por ano
ian_por_ano = df.groupby('Ano')['IAN'].mean()
print(f"IAN médio por ano:\n{ian_por_ano.round(3)}")

# % alunos com alguma defasagem (abs >= 1) por ano
risco_ano = df.groupby('Ano')['Risco_Defasagem'].mean() * 100
print(f"\n% alunos com defasagem por ano:\n{risco_ano.round(1)}")

# Defasagem média por ano e fase
defas_fase = df.groupby(['Ano', 'Fase_Num'])['Defasagem'].mean().unstack(level=0)
print(f"\nDefasagem média por Fase e Ano:\n{defas_fase.round(2)}")

# =============================================================================
# PERGUNTA 2: Desempenho acadêmico (IDA)
# O IDA está melhorando, estagnado ou caindo?
# =============================================================================
print("\n" + "="*60)
print("PERGUNTA 2: Desempenho acadêmico (IDA)")
print("="*60)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Boxplot IDA por ano
df.boxplot(column='IDA', by='Ano', ax=axes[0])
axes[0].set_title('IDA por Ano')
axes[0].set_ylabel('IDA (Indicador de Aprendizagem)')

# Mediana IDA por ano
ida_stats = df.groupby('Ano')['IDA'].agg(['mean', 'median', 'std'])
axes[1].plot(ida_stats.index, ida_stats['mean'], 'o-', label='Média', linewidth=2)
axes[1].plot(ida_stats.index, ida_stats['median'], 's--', label='Mediana', linewidth=2)
axes[1].fill_between(ida_stats.index,
                     ida_stats['mean'] - ida_stats['std'],
                     ida_stats['mean'] + ida_stats['std'], alpha=0.2)
axes[1].set_title('Evolução do IDA (Média ± DP)')
axes[1].set_xlabel('Ano')
axes[1].set_ylabel('IDA')
axes[1].legend()

plt.suptitle('Pergunta 2: Desempenho Acadêmico (IDA)', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'p2_ida_evolucao.png'), dpi=150, bbox_inches='tight')
plt.close()

print(f"IDA estatísticas por ano:\n{ida_stats.round(3)}")

# =============================================================================
# PERGUNTA 3: Engajamento × Desempenho (IEG × IDA × IPV)
# =============================================================================
print("\n" + "="*60)
print("PERGUNTA 3: Engajamento × Desempenho (IEG × IDA × IPV)")
print("="*60)

# Scatter IEG vs IDA colorido por IPV
fig, ax = plt.subplots(figsize=(10, 7))
df_valid = df.dropna(subset=['IEG', 'IDA', 'IPV'])
sc = ax.scatter(df_valid['IEG'], df_valid['IDA'], c=df_valid['IPV'],
                cmap='RdYlGn', alpha=0.5, s=15)
plt.colorbar(sc, label='IPV (Ponto de Virada)')
ax.set_xlabel('IEG (Engajamento)')
ax.set_ylabel('IDA (Aprendizagem)')
ax.set_title('Pergunta 3: IEG × IDA, colorido por IPV')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'p3_ieg_ida_ipv.png'), dpi=150, bbox_inches='tight')
plt.close()

# Correlações
corr_3 = df[['IEG', 'IDA', 'IPV']].corr()
print(f"Correlações IEG/IDA/IPV:\n{corr_3.round(3)}")

# =============================================================================
# PERGUNTA 4: Coerência da autoavaliação (IAA × IDA × IEG)
# =============================================================================
print("\n" + "="*60)
print("PERGUNTA 4: Autoavaliação (IAA × IDA × IEG)")
print("="*60)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Scatter IAA vs IDA
df_valid4 = df.dropna(subset=['IAA', 'IDA'])
axes[0].scatter(df_valid4['IAA'], df_valid4['IDA'], alpha=0.3, s=10, color='steelblue')
lim = [min(df_valid4[['IAA', 'IDA']].min()), max(df_valid4[['IAA', 'IDA']].max())]
axes[0].plot(lim, lim, 'r--', alpha=0.7, label='Linha de igualdade')
axes[0].set_xlabel('IAA (Autoavaliação)')
axes[0].set_ylabel('IDA (Desempenho Real)')
axes[0].set_title('Autoavaliação vs Desempenho Real')
axes[0].legend()

# Gap IAA - IDA por Pedra
df_valid4['Gap_IAA_IDA'] = df_valid4['IAA'] - df_valid4['IDA']
df_valid4.boxplot(column='Gap_IAA_IDA', by='Pedra', ax=axes[1])
axes[1].set_title('Gap (IAA - IDA) por Pedra')
axes[1].set_ylabel('IAA - IDA')
axes[1].axhline(y=0, color='red', linestyle='--', alpha=0.7)

plt.suptitle('Pergunta 4: Coerência da Autoavaliação', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'p4_autoavaliacao.png'), dpi=150, bbox_inches='tight')
plt.close()

gap_stats = df_valid4.groupby('Pedra')['Gap_IAA_IDA'].agg(['mean', 'median', 'std'])
print(f"Gap (IAA - IDA) por Pedra:\n{gap_stats.round(3)}")

# =============================================================================
# PERGUNTA 5: Padrões psicossociais que antecedem quedas (IPS)
# =============================================================================
print("\n" + "="*60)
print("PERGUNTA 5: Padrões psicossociais (IPS) e quedas de desempenho")
print("="*60)

# Para alunos rastreáveis entre anos: comparar IDA entre anos
# Merge alunos 2022->2023 e 2023->2024 pelo RA
resultados_delta = []
for ano_ant, ano_post in [(2022, 2023), (2023, 2024)]:
    df_ant = df[df['Ano'] == ano_ant][['RA', 'IDA', 'IPS', 'IEG', 'INDE']].rename(
        columns={'IDA': 'IDA_ant', 'IPS': 'IPS_ant', 'IEG': 'IEG_ant', 'INDE': 'INDE_ant'})
    df_post_yr = df[df['Ano'] == ano_post][['RA', 'IDA', 'IPS', 'INDE']].rename(
        columns={'IDA': 'IDA_post', 'IPS': 'IPS_post', 'INDE': 'INDE_post'})
    merged = df_ant.merge(df_post_yr, on='RA', how='inner')
    merged['Delta_IDA'] = merged['IDA_post'] - merged['IDA_ant']
    merged['Piorou'] = (merged['Delta_IDA'] < 0).astype(int)
    merged['Transicao'] = f'{ano_ant}->{ano_post}'
    resultados_delta.append(merged)

df_delta = pd.concat(resultados_delta, ignore_index=True)

fig, ax = plt.subplots(figsize=(10, 6))
df_delta_valid = df_delta.dropna(subset=['IPS_ant', 'Delta_IDA'])
ax.scatter(df_delta_valid['IPS_ant'], df_delta_valid['Delta_IDA'],
           c=df_delta_valid['Piorou'], cmap='RdYlGn_r', alpha=0.4, s=15)
ax.axhline(y=0, color='red', linestyle='--', alpha=0.7)
ax.set_xlabel('IPS no ano anterior')
ax.set_ylabel('Variação do IDA (ano seguinte - anterior)')
ax.set_title('Pergunta 5: IPS anterior vs Variação do IDA')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'p5_ips_delta_ida.png'), dpi=150, bbox_inches='tight')
plt.close()

ips_piorou = df_delta.groupby('Piorou')['IPS_ant'].mean()
print(f"IPS médio anterior:")
print(f"  Alunos que MELHORARAM IDA: {ips_piorou.get(0, 'N/A'):.3f}")
print(f"  Alunos que PIORARAM IDA:   {ips_piorou.get(1, 'N/A'):.3f}")

# =============================================================================
# PERGUNTA 6: Psicopedagógico vs. Defasagem (IPP × IAN)
# =============================================================================
print("\n" + "="*60)
print("PERGUNTA 6: Psicopedagógico (IPP) vs Defasagem (IAN)")
print("="*60)

fig, ax = plt.subplots(figsize=(10, 6))
df_valid6 = df.dropna(subset=['IPP', 'IAN'])
sc = ax.scatter(df_valid6['IPP'], df_valid6['IAN'], c=df_valid6['Defasagem'].abs(),
                cmap='RdYlGn_r', alpha=0.4, s=15)
plt.colorbar(sc, label='|Defasagem|')
ax.set_xlabel('IPP (Psicopedagógico)')
ax.set_ylabel('IAN (Adequação ao Nível)')
ax.set_title('Pergunta 6: IPP vs IAN, colorido por Defasagem')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'p6_ipp_ian.png'), dpi=150, bbox_inches='tight')
plt.close()

corr_6 = df[['IPP', 'IAN', 'Defasagem']].corr()
print(f"Correlação IPP/IAN/Defasagem:\n{corr_6.round(3)}")

# =============================================================================
# PERGUNTA 7: Ponto de virada (IPV)
# =============================================================================
print("\n" + "="*60)
print("PERGUNTA 7: Ponto de Virada (IPV)")
print("="*60)

# Indicadores por nível de IPV (tercis)
df_ipv = df.dropna(subset=['IPV']).copy()
df_ipv['IPV_Tercil'] = pd.qcut(df_ipv['IPV'], q=3, labels=['Baixo', 'Médio', 'Alto'])

indicadores = ['IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IAN']
ipv_profile = df_ipv.groupby('IPV_Tercil')[indicadores].mean()
print(f"Perfil médio por tercil de IPV:\n{ipv_profile.round(3)}")

fig, ax = plt.subplots(figsize=(10, 6))
ipv_profile.T.plot(kind='bar', ax=ax)
ax.set_title('Pergunta 7: Indicadores médios por tercil de IPV')
ax.set_xlabel('Indicador')
ax.set_ylabel('Valor médio')
ax.legend(title='IPV Tercil')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'p7_ipv_perfil.png'), dpi=150, bbox_inches='tight')
plt.close()

# =============================================================================
# PERGUNTA 8: Multidimensionalidade (INDE × combinações)
# =============================================================================
print("\n" + "="*60)
print("PERGUNTA 8: Multidimensionalidade dos indicadores no INDE")
print("="*60)

# Regressão linear para coeficientes normalizados
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

features_8 = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV']
df_reg = df.dropna(subset=features_8 + ['INDE'])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_reg[features_8])
y = df_reg['INDE'].values

lr = LinearRegression()
lr.fit(X_scaled, y)

coefs = pd.Series(lr.coef_, index=features_8).sort_values(ascending=False)
print(f"Coeficientes normalizados (influência no INDE):\n{coefs.round(4)}")
print(f"R² do modelo linear: {lr.score(X_scaled, y):.4f}")

fig, ax = plt.subplots(figsize=(10, 5))
coefs.plot(kind='barh', ax=ax, color=sns.color_palette('viridis', len(coefs)))
ax.set_xlabel('Coeficiente Normalizado')
ax.set_title('Pergunta 8: Contribuição relativa de cada indicador no INDE')
ax.axvline(x=0, color='black', linewidth=0.5)
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'p8_inde_coeficientes.png'), dpi=150, bbox_inches='tight')
plt.close()

# Heatmap de correlação
fig, ax = plt.subplots(figsize=(9, 7))
corr_all = df[features_8 + ['INDE']].corr()
sns.heatmap(corr_all, annot=True, fmt='.2f', cmap='RdYlBu_r', center=0, ax=ax)
ax.set_title('Heatmap de Correlação: Indicadores × INDE')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'p8_heatmap_correlacao.png'), dpi=150, bbox_inches='tight')
plt.close()

# =============================================================================
# PERGUNTA 10: Efetividade do programa por fase/pedra
# =============================================================================
print("\n" + "="*60)
print("PERGUNTA 10: Efetividade do programa")
print("="*60)

# Evolução de Pedra por ano (percentual)
pedra_ano = pd.crosstab(df['Ano'], df['Pedra'], normalize='index') * 100
print(f"Distribuição de Pedra por ano (%):\n{pedra_ano.round(1)}")

fig, ax = plt.subplots(figsize=(10, 6))
pedra_ano.plot(kind='bar', stacked=True, ax=ax, 
               color=['#e74c3c', '#f39c12', '#3498db', '#2ecc71'])
ax.set_title('Pergunta 10: Evolução da distribuição de Pedras por ano')
ax.set_ylabel('% dos alunos')
ax.set_xlabel('Ano')
ax.legend(title='Pedra')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'p10_pedras_evolucao.png'), dpi=150, bbox_inches='tight')
plt.close()

# Para alunos rastreáveis: transição de pedra
for ano_a, ano_b in [(2022, 2023), (2023, 2024)]:
    df_a = df[df['Ano'] == ano_a][['RA', 'Pedra_Num']].rename(columns={'Pedra_Num': 'Pedra_A'})
    df_b = df[df['Ano'] == ano_b][['RA', 'Pedra_Num']].rename(columns={'Pedra_Num': 'Pedra_B'})
    merged = df_a.merge(df_b, on='RA').dropna()
    merged['Transicao'] = merged['Pedra_B'] - merged['Pedra_A']
    melhorou = (merged['Transicao'] > 0).mean() * 100
    piorou = (merged['Transicao'] < 0).mean() * 100
    manteve = (merged['Transicao'] == 0).mean() * 100
    print(f"\nTransição {ano_a}->{ano_b} ({len(merged)} alunos):")
    print(f"  Subiram de pedra:   {melhorou:.1f}%")
    print(f"  Mantiveram:         {manteve:.1f}%")
    print(f"  Desceram de pedra:  {piorou:.1f}%")

# =============================================================================
# PERGUNTA 11: Insights criativos
# =============================================================================
print("\n" + "="*60)
print("PERGUNTA 11: Insights criativos")
print("="*60)

# 11a: Impacto do gênero
genero_stats = df.groupby('Genero')[['INDE', 'IDA', 'IEG', 'IPV']].mean()
print(f"\nMédias por gênero:\n{genero_stats.round(3)}")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
df.boxplot(column='INDE', by='Genero', ax=axes[0])
axes[0].set_title('INDE por Gênero')

# 11b: Anos no programa vs desempenho
anos_prog = df.groupby('Anos_No_Programa')['INDE'].mean()
axes[1].plot(anos_prog.index, anos_prog.values, 'o-', linewidth=2, color='teal')
axes[1].set_xlabel('Anos no Programa')
axes[1].set_ylabel('INDE Médio')
axes[1].set_title('INDE vs Tempo no Programa')

plt.suptitle('Pergunta 11: Insights Criativos', fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'p11_insights.png'), dpi=150, bbox_inches='tight')
plt.close()

# 11c: Instituição pública vs privada
inst_stats = df.groupby('Instituicao_Publica')[['INDE', 'IDA', 'IEG']].mean()
inst_stats.index = ['Privada/Outra', 'Pública']
print(f"\nMédias por tipo de instituição:\n{inst_stats.round(3)}")

print("\n" + "="*60)
print(f"ANÁLISE CONCLUÍDA! {len(os.listdir(PLOT_DIR))} gráficos salvos em {PLOT_DIR}")
print("="*60)
