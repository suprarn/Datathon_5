"""
01_eda_limpeza.py
=================
Fase 1 do Datathon: Carregamento, padronização e limpeza dos dados PEDE 2022-2024.
Gera df_unificado.parquet para uso nas fases seguintes.

Autor: Equipe Datathon Fase 5
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# 1. CONFIGURAÇÃO DE CAMINHOS
# =============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'Data')
EXCEL_PATH = os.path.join(DATA_DIR, 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data_processed')
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Base: {BASE_DIR}")
print(f"Excel: {EXCEL_PATH}")

# =============================================================================
# 2. CARREGAMENTO DAS 3 ABAS
# =============================================================================
print("\n" + "="*60)
print("CARREGANDO DADOS...")
print("="*60)

df_2022 = pd.read_excel(EXCEL_PATH, sheet_name='PEDE2022')
print(f"PEDE2022: {df_2022.shape}", flush=True)

df_2023 = pd.read_excel(EXCEL_PATH, sheet_name='PEDE2023')
print(f"PEDE2023: {df_2023.shape}", flush=True)

df_2024 = pd.read_excel(EXCEL_PATH, sheet_name='PEDE2024')
print(f"PEDE2024: {df_2024.shape}", flush=True)

# =============================================================================
# 3. PADRONIZAÇÃO DE COLUNAS
# =============================================================================
# Diagnóstico revelou diferenças importantes entre abas:
# - PEDE2022: Fase=int, 'Pedra 22', 'INDE 22', 'Defas', 'Fase ideal'
# - PEDE2023: Fase=str('ALFA','FASE 1'...), 'Pedra 2023', 'INDE 2023', 
#   'Defasagem', 'Fase Ideal', 'Agata' (sem acento)
# - PEDE2024: Fase=str, 'Pedra 2024', 'INDE 2024', 'Defasagem', 'Fase Ideal'

print("\nPADRONIZANDO COLUNAS...", flush=True)

# --- Mapeamento PEDE 2022 ---
rename_2022 = {
    'INDE 22': 'INDE',
    'Pedra 22': 'Pedra',
    'Fase ideal': 'Fase_Ideal',
    'Defas': 'Defasagem',
}

# --- Mapeamento PEDE 2023 ---
rename_2023 = {
    'INDE 2023': 'INDE',
    'Pedra 2023': 'Pedra',
    'Fase Ideal': 'Fase_Ideal',
}

# --- Mapeamento PEDE 2024 ---
rename_2024 = {
    'INDE 2024': 'INDE',
    'Pedra 2024': 'Pedra',
    'Fase Ideal': 'Fase_Ideal',
    'Escola': 'Escola',
    'Ativo/ Inativo': 'Status_Ativo',
}

# Mapeamento compartilhado (colunas com nome idêntico nas 3 abas)
rename_common = {
    'Nome Anonimizado': 'Nome',
    'Data de Nasc': 'Data_Nasc',
    'Gênero': 'Genero',
    'Ano ingresso': 'Ano_Ingresso',
    'Instituição de ensino': 'Instituicao_Ensino',
    'Nº Av': 'Num_Avaliacoes',
    'Rec Av1': 'Rec_Av1',
    'Rec Av2': 'Rec_Av2',
    'Rec Psicologia': 'Rec_Psicologia',
    'Indicado': 'Indicado_Bolsa',
    'Atingiu PV': 'Atingiu_PV',
    'Destaque IEG': 'Destaque_IEG',
    'Destaque IDA': 'Destaque_IDA',
    'Destaque IPV': 'Destaque_IPV',
    'Mat': 'Nota_Mat',
    'Por': 'Nota_Por',
    'Ing': 'Nota_Ing',
}

# Colunas finais que vamos manter
COLUNAS_FINAIS = [
    'RA', 'Ano', 'Fase', 'Turma', 'Nome', 'Data_Nasc', 'Idade', 'Genero',
    'Ano_Ingresso', 'Instituicao_Ensino',
    'INDE', 'Pedra', 'IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV',
    'Nota_Mat', 'Nota_Por', 'Nota_Ing',
    'Cg', 'Cf', 'Ct', 'Num_Avaliacoes',
    'Indicado_Bolsa', 'Atingiu_PV',
    'Fase_Ideal', 'Defasagem',
    'Destaque_IEG', 'Destaque_IDA', 'Destaque_IPV',
    'Rec_Psicologia',
]


def padronizar_aba(df, rename_especifico, ano):
    """Renomeia colunas de uma aba e adiciona coluna Ano."""
    # Merge de renomeações: específicas + comuns
    rename_full = {**rename_common, **rename_especifico}
    
    # Filtrar apenas colunas que existem
    rename_valido = {k: v for k, v in rename_full.items() if k in df.columns}
    df_r = df.rename(columns=rename_valido)
    df_r['Ano'] = ano
    
    # Manter apenas colunas padronizadas existentes
    cols = [c for c in COLUNAS_FINAIS if c in df_r.columns]
    return df_r[cols]


df_2022_p = padronizar_aba(df_2022, rename_2022, 2022)
df_2023_p = padronizar_aba(df_2023, rename_2023, 2023)
df_2024_p = padronizar_aba(df_2024, rename_2024, 2024)

print(f"2022 padronizado: {df_2022_p.shape}")
print(f"2023 padronizado: {df_2023_p.shape}")
print(f"2024 padronizado: {df_2024_p.shape}")

# =============================================================================
# 4. PADRONIZAÇÃO DA COLUNA FASE
# =============================================================================
# PEDE2022: Fase é int (0,1,2,...,7) — representa o nº da fase
# PEDE2023/2024: Fase é str ('ALFA', 'FASE 1', ..., 'FASE 7')
# Problema: se algum valor no 2022 não foi mapeado, ficava como turma (1A, 2B, etc.)

print("\nPADRONIZANDO COLUNA FASE...", flush=True)

fase_map_int = {
    0: 'ALFA', 1: 'FASE 1', 2: 'FASE 2', 3: 'FASE 3',
    4: 'FASE 4', 5: 'FASE 5', 6: 'FASE 6', 7: 'FASE 7', 8: 'FASE 8'
}

# Converter 2022 de int para str
df_2022_p['Fase'] = df_2022_p['Fase'].map(fase_map_int).fillna(df_2022_p['Fase'].astype(str))

# Normalizar todas as fases para maiúsculas sem espaços extras
for df_temp in [df_2022_p, df_2023_p, df_2024_p]:
    df_temp['Fase'] = df_temp['Fase'].astype(str).str.strip().str.upper()

# FIX: Normalizar valores de Fase que ficaram como códigos de turma (1A, 2B, etc.)
# Extrair o número da fase a partir de códigos residuais
def normalizar_fase(fase_val):
    """Converte valores residuais de turma para nome de fase padronizado."""
    if fase_val in ['ALFA', 'FASE 1', 'FASE 2', 'FASE 3', 'FASE 4',
                    'FASE 5', 'FASE 6', 'FASE 7', 'FASE 8']:
        return fase_val
    # Tentar extrair número do início (ex: '1A' -> 1, '2B' -> 2)
    import re
    match = re.match(r'^(\d+)', str(fase_val))
    if match:
        num = int(match.group(1))
        if num == 0:
            return 'ALFA'
        elif 1 <= num <= 8:
            return f'FASE {num}'
        elif num == 9:
            return 'FASE 8'  # Fase 9 -> agrupar com FASE 8
    return fase_val  # Fallback

for df_temp in [df_2022_p, df_2023_p, df_2024_p]:
    df_temp['Fase'] = df_temp['Fase'].apply(normalizar_fase)

# =============================================================================
# 5. CONCATENAÇÃO
# =============================================================================
print("\nCONCATENANDO...", flush=True)

df_all = pd.concat([df_2022_p, df_2023_p, df_2024_p], ignore_index=True)
print(f"Unificado: {df_all.shape[0]} linhas x {df_all.shape[1]} colunas")
print(f"Alunos por ano:\n{df_all['Ano'].value_counts().sort_index().to_string()}")

# =============================================================================
# 6. CONVERSÃO DE TIPOS
# =============================================================================
print("\nCONVERTENDO TIPOS...", flush=True)

# 6.1 INDE para float
df_all['INDE'] = pd.to_numeric(df_all['INDE'], errors='coerce')

# 6.2 Todos os indicadores numéricos
cols_numericas = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV',
                  'Nota_Mat', 'Nota_Por', 'Nota_Ing',
                  'Cg', 'Cf', 'Ct', 'Indicado_Bolsa', 'Atingiu_PV',
                  'Defasagem', 'Num_Avaliacoes']
for col in cols_numericas:
    if col in df_all.columns:
        df_all[col] = pd.to_numeric(df_all[col], errors='coerce')

# 6.3 Padronizar valores de Pedra (PEDE2023 tem 'Agata' sem acento)
if 'Pedra' in df_all.columns:
    pedra_fix = {
        'Agata': 'Ágata',
        'agata': 'Ágata',
        'AGATA': 'Ágata',
        'ÁGATA': 'Ágata',
        'QUARTZO': 'Quartzo',
        'AMETISTA': 'Ametista',
        'TOPÁZIO': 'Topázio',
        'TOPAZIO': 'Topázio',
    }
    df_all['Pedra'] = df_all['Pedra'].replace(pedra_fix)
    
    pedra_order = ['Quartzo', 'Ágata', 'Ametista', 'Topázio']
    df_all['Pedra'] = pd.Categorical(df_all['Pedra'], categories=pedra_order, ordered=True)

# 6.4 Data de nascimento
if 'Data_Nasc' in df_all.columns:
    df_all['Data_Nasc'] = pd.to_datetime(df_all['Data_Nasc'], errors='coerce')

# 6.5 Gênero padronizado — FIX: normalizar 'Menino'→'Masculino', 'Menina'→'Feminino'
if 'Genero' in df_all.columns:
    df_all['Genero'] = df_all['Genero'].astype(str).str.strip().str.capitalize()
    genero_fix = {'Menino': 'Masculino', 'Menina': 'Feminino'}
    df_all['Genero'] = df_all['Genero'].replace(genero_fix)

print("Tipos convertidos OK")

# =============================================================================
# 7. REMOÇÃO DE DUPLICATAS
# =============================================================================
print("\nDUPLICATAS...", flush=True)
n_antes = len(df_all)
df_all = df_all.drop_duplicates(subset=['RA', 'Ano'], keep='first')
print(f"Antes: {n_antes} | Depois: {len(df_all)} | Removidos: {n_antes - len(df_all)}")

# =============================================================================
# 8. FEATURE ENGINEERING
# =============================================================================
print("\nFEATURE ENGINEERING...", flush=True)

# 8.1 Anos no programa
df_all['Anos_No_Programa'] = df_all['Ano'] - df_all['Ano_Ingresso']
df_all['Anos_No_Programa'] = df_all['Anos_No_Programa'].clip(lower=0)

# 8.2 Instituição pública
if 'Instituicao_Ensino' in df_all.columns:
    df_all['Instituicao_Publica'] = df_all['Instituicao_Ensino'].astype(str).str.lower().str.contains(
        'pública|publica|estadual|municipal', na=False
    ).astype(int)

# 8.3 Avaliação completa
indicadores_core = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV']
cols_exist = [c for c in indicadores_core if c in df_all.columns]
df_all['Avaliacao_Completa'] = (~df_all[cols_exist].isna().any(axis=1)).astype(int)

# 8.4 Pedra numérica
pedra_num = {'Quartzo': 1, 'Ágata': 2, 'Ametista': 3, 'Topázio': 4}
df_all['Pedra_Num'] = df_all['Pedra'].map(pedra_num)

# 8.5 Fase numérica
def fase_para_num(f):
    if pd.isna(f): return np.nan
    s = str(f).upper().strip()
    if 'ALFA' in s: return 0
    for i in range(9, 0, -1):
        if str(i) in s: return i
    return np.nan

df_all['Fase_Num'] = df_all['Fase'].apply(fase_para_num)

# 8.6 Risco de defasagem (variável-alvo ML)
# FIX: Defasagem negativa = aluno ABAIXO do nível ideal = risco real
# Defasagem positiva = aluno ACIMA do nível ideal = não é risco
# Usamos Defasagem < 0 (abaixo do ideal) como indicador de risco
df_all['Risco_Defasagem'] = (df_all['Defasagem'] < 0).astype(int)

# 8.7 Genero numérico para ML
df_all['Genero_Num'] = df_all['Genero'].map({'Masculino': 0, 'Feminino': 1}).fillna(-1).astype(int)

print("Features criadas: Anos_No_Programa, Instituicao_Publica, Avaliacao_Completa, "
      "Pedra_Num, Fase_Num, Risco_Defasagem, Genero_Num")

# =============================================================================
# 9. RELATÓRIO DE QUALIDADE
# =============================================================================
print("\n" + "="*60)
print("RELATÓRIO DE QUALIDADE DOS DADOS")
print("="*60)

# Missing values
print("\n--- Missing values (top 15) ---")
miss = df_all.isnull().sum()
miss_pct = (miss / len(df_all) * 100).round(1)
miss_df = pd.DataFrame({'N': miss, '%': miss_pct})
miss_df = miss_df[miss_df['N'] > 0].sort_values('%', ascending=False)
print(miss_df.head(15).to_string())

# INDE por ano
print("\n--- INDE por ano ---")
print(df_all.groupby('Ano')['INDE'].describe()[['count','mean','std','min','max']].round(2).to_string())

# Pedra por ano
print("\n--- Pedra por ano ---")
print(pd.crosstab(df_all['Ano'], df_all['Pedra'], dropna=False).to_string())

# Defasagem por ano
print("\n--- Defasagem por ano ---")
print(df_all.groupby('Ano')['Defasagem'].describe()[['count','mean','std','min','max']].round(2).to_string())

# Risco
print("\n--- Risco de Defasagem por ano ---")
print(df_all.groupby('Ano')['Risco_Defasagem'].mean().round(3).to_string())

# Fases
print("\n--- Fases encontradas ---")
print(df_all['Fase'].value_counts().sort_index().to_string())

# Correlações core
print("\n--- Correlações com INDE ---")
corr_cols = [c for c in ['IAN','IDA','IEG','IAA','IPS','IPP','IPV'] if c in df_all.columns]
corr = df_all[corr_cols + ['INDE']].corr()['INDE'].drop('INDE').sort_values(ascending=False)
print(corr.round(3).to_string())

# =============================================================================
# 10. SALVAMENTO
# =============================================================================
print("\n" + "="*60)
print("SALVANDO...")
print("="*60)

# Converter colunas object com tipos mistos (int + str) para str puro
# Isso evita ArrowTypeError ao salvar em parquet
for col in df_all.select_dtypes(include='object').columns:
    df_all[col] = df_all[col].astype(str).replace('nan', np.nan).replace('None', np.nan)

# Parquet unificado
out_parquet = os.path.join(OUTPUT_DIR, 'df_unificado.parquet')
df_all.to_parquet(out_parquet, index=False)
print(f"Parquet: {out_parquet} ({os.path.getsize(out_parquet)/1024:.0f} KB)")

# CSV (para inspeção fácil)
out_csv = os.path.join(OUTPUT_DIR, 'df_unificado.csv')
df_all.to_csv(out_csv, index=False, encoding='utf-8-sig')
print(f"CSV: {out_csv} ({os.path.getsize(out_csv)/1024:.0f} KB)")

# Individuais por ano
for ano in [2022, 2023, 2024]:
    df_ano = df_all[df_all['Ano'] == ano]
    p = os.path.join(OUTPUT_DIR, f'df_{ano}.parquet')
    df_ano.to_parquet(p, index=False)
    print(f"df_{ano}: {df_ano.shape[0]} linhas")

print(f"\nETL CONCLUÍDO! {len(df_all)} registros, {len(df_all.columns)} colunas.")
print(f"Colunas: {list(df_all.columns)}")
