import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import time
import os

# --- CONFIGURATION ---
CSV_PATH = r"C:\testage\dataset_34_features.csv"
MODEL_FILENAME = "xgboost_readmission_model.json"
TARGET_COL = 'label_readmission'


def get_data():
    print(f"📂 Chargement de {CSV_PATH} ...")
    start_time = time.time()

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"❌ Fichier introuvable : {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    # Suppression des colonnes inutiles
    cols_to_drop = ['encounter_id', 'patient_id', 'start_date']
    cols_to_drop = [c for c in cols_to_drop if c in df.columns]

    if cols_to_drop:
        print(f"🧹 Suppression des colonnes inutiles : {cols_to_drop}")
        df = df.drop(columns=cols_to_drop)

    print(f"✅ Données prêtes : {df.shape[0]} patients, {df.shape[1]} colonnes.")
    return df


def train_model():
    # 1. Chargement
    df = get_data()

    # 2. Vérification Target
    if TARGET_COL not in df.columns:
        raise ValueError(f"❌ Erreur : La colonne '{TARGET_COL}' est absente !")

    # 3. Préparation
    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]

    # 4. Split
    print("✂️ Séparation Train/Test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 5. Config GPU
    print(f"🚀 Initialisation de XGBoost sur GPU...")
    model = xgb.XGBClassifier(
        device="cuda",
        tree_method="hist",
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='binary:logistic',
        eval_metric='auc',
        early_stopping_rounds=50,
        missing=float('nan')
    )

    # 6. Entraînement
    print("🔥 Lancement de l'entraînement...")
    start_train = time.time()

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=100
    )

    print(f"✅ Entraînement terminé en {time.time() - start_train:.2f} secondes.")

    # 7. Évaluation
    # Note : Le warning "falling back to prediction using DMatrix" est normal ici,
    # car tes données de test sont sur le CPU (RAM) et le modèle sur GPU. C'est sans gravité.
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    auc = roc_auc_score(y_test, y_prob)
    acc = accuracy_score(y_test, y_pred)

    print(f"\n📊 --- RÉSULTATS ---")
    print(f"   • AUC Score : {auc:.4f}")
    print(f"   • Accuracy  : {acc:.4f}")
    print("\n   • Rapport détaillé :")
    print(classification_report(y_test, y_pred))

    # 8. Sauvegarde (CORRECTION DU BUG ICI)
    # On utilise .get_booster() pour sauvegarder le coeur du modèle proprement
    model.get_booster().save_model(MODEL_FILENAME)
    print(f"💾 Modèle sauvegardé avec succès sous : {MODEL_FILENAME}")


if __name__ == "__main__":
    train_model()