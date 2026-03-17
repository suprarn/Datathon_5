"""
03_modelo_preditivo.py
======================
Fase 3 do Datathon: Modelo preditivo de risco de defasagem.
Pipeline: feature engineering → treino/teste → comparação de modelos → avaliação → SHAP → salvamento.

Autor: Equipe Datathon Fase 5
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (classification_report, confusion_matrix, roc_auc_score,
                             roc_curve, f1_score, accuracy_score, precision_score,
                             recall_score)

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data_processed')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
PLOT_DIR = os.path.join(BASE_DIR, 'plots')
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

RANDOM_STATE = 42

# =============================================================================
# 1. CARREGAMENTO DOS DADOS
# =============================================================================
print("="*60)
print("MODELO PREDITIVO DE RISCO DE DEFASAGEM")
print("="*60)

df = pd.read_parquet(os.path.join(DATA_DIR, 'df_unificado.parquet'))
print(f"Dados carregados: {df.shape}")

# =============================================================================
# 2. DEFINIÇÃO DA VARIÁVEL-ALVO E FEATURES
# =============================================================================
print("\n--- Definição do problema ---")

# Variável-alvo: Risco_Defasagem (1 = defasagem abs >= 1, 0 = sem defasagem)
target = 'Risco_Defasagem'

# Features selecionadas para o modelo
# NOTA: INDE foi REMOVIDO para evitar data leakage — o INDE é combinação
# linear perfeita dos sub-indicadores (R²=1.0), então incluí-lo junto com
# IAN, IDA, IEG etc. faria o modelo "trapacear".
# NOTA 2: IAN também foi REMOVIDO — ele é derivado diretamente da Defasagem
# (IAN mede adequação ao nível, que é essencialmente o inverso da defasagem).
# Incluí-lo como feature resultava em F1=1.0 (leakage perfeito).
# O modelo deve prever risco a partir de indicadores comportamentais e acadêmicos.
FEATURES = [
    'IDA', 'IEG', 'IAA', 'IPS', 'IPP', 'IPV',                   # Indicadores (sem IAN)
    'Nota_Mat', 'Nota_Por',                                       # Notas disciplinas
    'Fase_Num',                                                    # Fase numérica
    'Anos_No_Programa',                                            # Tempo no programa
    'Instituicao_Publica',                                         # Tipo de escola
    'Genero_Num',                                                  # Gênero
    'Num_Avaliacoes',                                              # Qtd avaliações
]

# Filtrar apenas linhas com target definido
df_model = df.dropna(subset=[target]).copy()
print(f"Registros com target válido: {len(df_model)}")

# Verificar distribuição da classe
print(f"\nDistribuição da classe {target}:")
print(df_model[target].value_counts())
print(f"% Classe 1 (risco): {df_model[target].mean()*100:.1f}%")

# =============================================================================
# 3. SEPARAÇÃO TREINO/TESTE
# =============================================================================
print("\n--- Separação treino/teste ---")

# Estratégia: treinar com 2022+2023, testar com 2024 (simulação temporal)
df_train = df_model[df_model['Ano'].isin([2022, 2023])].copy()
df_test = df_model[df_model['Ano'] == 2024].copy()

# Verificar features disponíveis
features_disponiveis = [f for f in FEATURES if f in df_model.columns]
print(f"Features usadas ({len(features_disponiveis)}): {features_disponiveis}")

X_train = df_train[features_disponiveis]
y_train = df_train[target]
X_test = df_test[features_disponiveis]
y_test = df_test[target]

print(f"Treino: {X_train.shape[0]} amostras (2022+2023)")
print(f"Teste:  {X_test.shape[0]} amostras (2024)")
print(f"Classe 1 no treino: {y_train.mean()*100:.1f}%")
print(f"Classe 1 no teste:  {y_test.mean()*100:.1f}%")

# =============================================================================
# 4. PIPELINE DE MODELAGEM
# =============================================================================
print("\n--- Treinando modelos ---")

# Definir pipelines para cada modelo
modelos = {
    'Regressão Logística': Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('clf', LogisticRegression(random_state=RANDOM_STATE, max_iter=1000,
                                    class_weight='balanced'))
    ]),
    'Random Forest': Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('clf', RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE,
                                        class_weight='balanced', max_depth=10,
                                        min_samples_split=5))
    ]),
    'Gradient Boosting': Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('clf', GradientBoostingClassifier(n_estimators=200, random_state=RANDOM_STATE,
                                           max_depth=5, learning_rate=0.1,
                                           min_samples_split=5))
    ]),
}

# Treinar e avaliar cada modelo
resultados = {}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

for nome, pipeline in modelos.items():
    print(f"\n  Treinando {nome}...", flush=True)
    
    # Cross-validation no treino
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring='roc_auc')
    
    # Treinar no treino completo
    pipeline.fit(X_train, y_train)
    
    # Predições
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    
    # Métricas
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    
    resultados[nome] = {
        'pipeline': pipeline,
        'cv_auc_mean': cv_scores.mean(),
        'cv_auc_std': cv_scores.std(),
        'accuracy': acc,
        'precision': prec,
        'recall': rec,
        'f1': f1,
        'roc_auc': auc,
        'y_pred': y_pred,
        'y_proba': y_proba,
    }
    
    print(f"    CV AUC: {cv_scores.mean():.3f} (±{cv_scores.std():.3f})")
    print(f"    Test -> Acc: {acc:.3f} | Prec: {prec:.3f} | Rec: {rec:.3f} | F1: {f1:.3f} | AUC: {auc:.3f}")

# =============================================================================
# 5. COMPARAÇÃO DE MODELOS
# =============================================================================
print("\n" + "="*60)
print("COMPARAÇÃO DE MODELOS")
print("="*60)

# Tabela comparativa
metricas_cols = ['cv_auc_mean', 'cv_auc_std', 'accuracy', 'precision', 'recall', 'f1', 'roc_auc']
df_resultados = pd.DataFrame({nome: {m: resultados[nome][m] for m in metricas_cols}
                                for nome in resultados}).T
print(df_resultados.round(3).to_string())

# Selecionar melhor modelo (critério: F1 → empate: AUC)
melhor_nome = df_resultados['f1'].idxmax()
melhor = resultados[melhor_nome]
print(f"\nMelhor modelo: {melhor_nome} (F1={melhor['f1']:.3f}, AUC={melhor['roc_auc']:.3f})")

# =============================================================================
# 6. AVALIAÇÃO DETALHADA DO MELHOR MODELO
# =============================================================================
print("\n" + "="*60)
print(f"AVALIAÇÃO DETALHADA: {melhor_nome}")
print("="*60)

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, melhor['y_pred'], target_names=['Sem Risco', 'Em Risco']))

# Matriz de Confusão
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

cm = confusion_matrix(y_test, melhor['y_pred'])
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0],
            xticklabels=['Sem Risco', 'Em Risco'],
            yticklabels=['Sem Risco', 'Em Risco'])
axes[0].set_xlabel('Predito')
axes[0].set_ylabel('Real')
axes[0].set_title(f'Matriz de Confusão - {melhor_nome}')

# Curvas ROC comparativas
for nome, res in resultados.items():
    fpr, tpr, _ = roc_curve(y_test, res['y_proba'])
    axes[1].plot(fpr, tpr, label=f"{nome} (AUC={res['roc_auc']:.3f})")
axes[1].plot([0, 1], [0, 1], 'k--', alpha=0.5)
axes[1].set_xlabel('Taxa de Falso Positivo')
axes[1].set_ylabel('Taxa de Verdadeiro Positivo')
axes[1].set_title('Curvas ROC Comparativas')
axes[1].legend(loc='lower right')

plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'p9_modelo_avaliacao.png'), dpi=150, bbox_inches='tight')
plt.close()

# =============================================================================
# 7. IMPORTÂNCIA DAS FEATURES
# =============================================================================
print("\n--- Importância das Features ---")

# Feature importance do melhor modelo
if hasattr(melhor['pipeline']['clf'], 'feature_importances_'):
    importances = melhor['pipeline']['clf'].feature_importances_
elif hasattr(melhor['pipeline']['clf'], 'coef_'):
    importances = np.abs(melhor['pipeline']['clf'].coef_[0])
else:
    importances = np.zeros(len(features_disponiveis))

feat_imp = pd.Series(importances, index=features_disponiveis).sort_values(ascending=False)
print(feat_imp.round(4).to_string())

fig, ax = plt.subplots(figsize=(10, 6))
feat_imp.sort_values().plot(kind='barh', ax=ax, color=sns.color_palette('viridis', len(feat_imp)))
ax.set_xlabel('Importância')
ax.set_title(f'Importância das Features - {melhor_nome}')
plt.tight_layout()
plt.savefig(os.path.join(PLOT_DIR, 'p9_feature_importance.png'), dpi=150, bbox_inches='tight')
plt.close()

# =============================================================================
# 8. SALVAMENTO DO MODELO
# =============================================================================
print("\n" + "="*60)
print("SALVANDO MODELO...")
print("="*60)

modelo_path = os.path.join(MODEL_DIR, 'modelo_risco_defasagem.joblib')
joblib.dump(melhor['pipeline'], modelo_path)
print(f"Pipeline salvo: {modelo_path}")

# Salvar metadados do modelo
metadata = {
    'nome': melhor_nome,
    'features': features_disponiveis,
    'metricas': {m: float(melhor[m]) for m in metricas_cols},
    'target': target,
    'treino_anos': [2022, 2023],
    'teste_ano': 2024,
    'treino_n': len(X_train),
    'teste_n': len(X_test),
}

import json
meta_path = os.path.join(MODEL_DIR, 'modelo_metadata.json')
with open(meta_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
print(f"Metadados salvos: {meta_path}")

# Salvar tabela de resultados
df_resultados.to_csv(os.path.join(MODEL_DIR, 'comparacao_modelos.csv'))
print(f"Comparação salva: {os.path.join(MODEL_DIR, 'comparacao_modelos.csv')}")

# Salvar lista de features e importâncias
feat_imp.to_csv(os.path.join(MODEL_DIR, 'feature_importances.csv'))

print(f"\nMODELO PREDITIVO CONCLUÍDO!")
print(f"  Melhor modelo: {melhor_nome}")
print(f"  F1-Score: {melhor['f1']:.3f}")
print(f"  ROC-AUC: {melhor['roc_auc']:.3f}")
print(f"  Recall: {melhor['recall']:.3f}")
