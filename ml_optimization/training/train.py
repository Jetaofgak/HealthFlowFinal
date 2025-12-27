# %%
# CELL 1: Imports
import pandas as pd
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report, f1_score
import time
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

"""
TRAINING SCRIPT
---------------
This script is responsible for training the FINAL production model using the best hyperparameters
found during the Optuna optimization phase (see optuna_grid_search.py).

It performs:
1. Data Loading & Preprocessing
2. Model Initialization (with specific optimized params)
3. Training on the full training set
4. Detailed Evaluation (Confusion Matrix, ROC-AUC, Feature Importance)
5. Saving the model for the backend API
"""

# %%
# CELL 2: Configuration
CSV_PATH = r"../../dataset_with_nlp_features.csv"  # Encounter-level dataset (146K samples) - reduces overfitting
MODEL_FILENAME = "adaboost_readmission_model.pkl"  # Updated to AdaBoost
TARGET_COL = 'label_readmission'

# Optuna-optimized hyperparameters (Trial #155)
# NOTE: These values are copied from the output of `optuna_grid_search.py`
# We use the parameters that gave the best balance of High Validation F1 and Low Overfitting Gap.
# Val F1: 0.7778, Gap: 0.0251 (Excellent generalization!)
BEST_N_ESTIMATORS = 119
BEST_LEARNING_RATE = 0.43756465809513756

print(f"📋 Configuration: AdaBoost Model")
print(f"   Target: {TARGET_COL}")
print(f"   Hyperparameters from Optuna Trial #155:")
print(f"   - n_estimators: {BEST_N_ESTIMATORS}")
print(f"   - learning_rate: {BEST_LEARNING_RATE:.4f}")


# %%
# CELL 3: Load Raw Data & Preprocess (Using Shared Loader)
import time
from utils.data_loader import load_and_preprocess_data, get_train_val_test_splits

print(f"📂 Chargement de {CSV_PATH} ...")
start_time = time.time()

# AdaBoost requires imputed data (sklearn model cannot handle NaN)
df, _ = load_and_preprocess_data(CSV_PATH, TARGET_COL, impute_missing=True)
X_train, X_val, X_test, y_train, y_val, y_test = get_train_val_test_splits(df, TARGET_COL)

print(f"✅ Dataset chargé et divisé en {time.time() - start_time:.2f}s")
print(f"✅ Train: {X_train.shape[0]} | Val: {X_val.shape[0]} | Test: {X_test.shape[0]}")
print(f"📊 Features: {X_train.shape[1]}")
print(f"📊 Train distribution:\n{y_train.value_counts(normalize=True).round(3)}")
print(f"📊 Val distribution:\n{y_val.value_counts(normalize=True).round(3)}")



# %%
# CELL 4: Model Configuration
print(f"🚀 Initialisation de AdaBoost avec hyperparamètres optimisés...")

model = AdaBoostClassifier(
    n_estimators=BEST_N_ESTIMATORS,
    learning_rate=BEST_LEARNING_RATE,
    random_state=42,
    algorithm='SAMME.R'  # Real AdaBoost for probability estimates
)

print("✅ Modèle AdaBoost configuré!")
print(f"   - Type: AdaBoostClassifier")
print(f"   - Source: Optuna optimization (Trial #155)")
print(f"   - Expected Val F1: ~0.78")
print(f"   - Expected Gap: ~0.03 (Excellent generalization)")


# %%
# CELL 5: Training on Train Set
print("🔥 === ENTRAÎNEMENT ===\n")
start_train = time.time()

print("Training AdaBoost on training set...")
model.fit(X_train, y_train)

train_time = time.time() - start_train
print(f"✅ Entraînement terminé en {train_time:.2f}s")
print(f"📊 Model trained with {BEST_N_ESTIMATORS} estimators")


# %%
# CELL 6: Evaluate on Train and Validation Sets
print("\n📊 === ÉVALUATION TRAIN/VAL ===\n")

# Predictions on train and val
y_train_pred = model.predict(X_train)
y_val_pred = model.predict(X_val)

# Probabilities for AUC
y_train_prob = model.predict_proba(X_train)[:, 1]
y_val_prob = model.predict_proba(X_val)[:, 1]

# Calculate metrics
train_f1 = f1_score(y_train, y_train_pred)
val_f1 = f1_score(y_val, y_val_pred)
train_auc = roc_auc_score(y_train, y_train_prob)
val_auc = roc_auc_score(y_val, y_val_prob)

gap_f1 = abs(train_f1 - val_f1)
gap_auc = abs(train_auc - val_auc)
# The 'Gap' is a crucial metric:
# Small gap (< 0.05) = Good generalization
# Large gap (> 0.10) = Overfitting (model memorized training data)

print(f"Train F1:  {train_f1:.4f}")
print(f"Val F1:    {val_f1:.4f}")
print(f"Gap F1:    {gap_f1:.4f}")
print(f"\nTrain AUC: {train_auc:.4f}")
print(f"Val AUC:   {val_auc:.4f}")
print(f"Gap AUC:   {gap_auc:.4f}")

# %%
# CELL 7: Feature Importance Visualization
print("\n📊 === FEATURE IMPORTANCE ===\n")

feature_imp = pd.DataFrame({
    'feature': X_train.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False).head(15)

print("Top 15 Important Features:")
print(feature_imp.to_string(index=False))

plt.figure(figsize=(12, 8))
sns.barplot(data=feature_imp, y='feature', x='importance', palette='viridis')
plt.title('Top 15 Feature Importances - AdaBoost Model', fontsize=14, fontweight='bold')
plt.xlabel('Importance')
plt.ylabel('Feature')
plt.tight_layout()
plt.show()


# %%
# CELL 15: Generate Predictions
print("🔮 === GÉNÉRATION DES PRÉDICTIONS ===\n")

# Binary predictions (0 or 1)
y_pred = model.predict(X_test)

# Probability predictions for ROC curve
y_prob = model.predict_proba(X_test)[:, 1]

print(f"✅ Predictions generated: {len(y_pred)} samples")
print(f"📊 Prediction distribution:\n{pd.Series(y_pred).value_counts()}")

# Calculate metrics
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report, confusion_matrix

accuracy = accuracy_score(y_test, y_pred)
test_auc = roc_auc_score(y_test, y_prob)
test_f1 = f1_score(y_test, y_pred)

print(f"\n🎯 Test Accuracy: {accuracy:.4f}")
print(f"📈 Test F1-Score: {test_f1:.4f}")
print(f"📈 Test ROC-AUC: {test_auc:.4f}")
print(f"\n📋 Classification Report:")
print(classification_report(y_test, y_pred, target_names=['No Readmission', 'Readmission']))

# Generate and visualize confusion matrix
print(f"\n🔲 === CONFUSION MATRIX ===\n")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# Visualize confusion matrix
plt.figure(figsize=(10, 8))
sns.heatmap(
    cm, 
    annot=True, 
    fmt='d', 
    cmap='Blues',
    xticklabels=['No Readmission', 'Readmission'],
    yticklabels=['No Readmission', 'Readmission'],
    cbar_kws={'label': 'Count'}
)
plt.title('Confusion Matrix - Test Set', fontsize=16, fontweight='bold')
plt.ylabel('Actual', fontsize=12)
plt.xlabel('Predicted', fontsize=12)
plt.tight_layout()
plt.show()

# Calculate and display confusion matrix metrics
tn, fp, fn, tp = cm.ravel()
print(f"\n📊 Confusion Matrix Breakdown:")
print(f"   True Negatives (TN):  {tn:>6} - Correctly predicted No Readmission")
print(f"   False Positives (FP): {fp:>6} - Incorrectly predicted Readmission")
print(f"   False Negatives (FN): {fn:>6} - Missed Readmissions")
print(f"   True Positives (TP):  {tp:>6} - Correctly predicted Readmission")

# Calculate additional metrics
sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
test_f1_manual = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0

print(f"\n📈 Additional Metrics:")
print(f"   Sensitivity (Recall): {sensitivity:.4f} - % of actual readmissions caught")
print(f"   Specificity:          {specificity:.4f} - % of non-readmissions correctly identified")
print(f"   Precision:            {precision:.4f} - % of predicted readmissions that are correct")
print(f"   F1-Score (manual):    {test_f1_manual:.4f} - Harmonic mean of precision and recall")
print(f"   F1-Score (sklearn):   {test_f1:.4f} - Should match manual calculation")


# %%
# CELL 8: Save Model
print("\n💾 === SAUVEGARDE DU MODÈLE ===\n")

joblib.dump(model, MODEL_FILENAME)
print(f"✅ Modèle sauvegardé: {MODEL_FILENAME}")
print(f"   Type: AdaBoostClassifier")
print(f"   Hyperparameters: n_estimators={BEST_N_ESTIMATORS}, learning_rate={BEST_LEARNING_RATE:.4f}")
print(f"   Val F1: {val_f1:.4f}")
print(f"   Gap: {gap_f1:.4f}")

print("\n🎉 Pipeline AdaBoost terminé!")
print("\n📊 FINAL METRICS SUMMARY:")
print(f"   Train F1: {train_f1:.4f} | Val F1: {val_f1:.4f} | Test F1: {test_f1:.4f}")
print(f"   Train AUC: {train_auc:.4f} | Val AUC: {val_auc:.4f} | Test AUC: {test_auc:.4f}")
print(f"   Overfitting Gap (F1): {gap_f1:.4f}")
print(f"\n✅ Model ready for deployment to ml-predictor service")



