import xgboost as xgb
import pandas as pd
import numpy as np

# 1. Charger le modèle
print("🔄 Chargement du modèle...")
model = xgb.Booster()
model.load_model("xgboost_readmission_model.json")
print("✅ Modèle chargé avec succès !")

# 2. Définir les noms EXACTS des features attendues (copiés depuis ton erreur)
features = [
    'age', 'gender_male', 'race_white', 'race_black',
    'feat_diabetes', 'feat_hypertension', 'feat_heart_failure', 'feat_respiratory',
    'feat_renal', 'feat_anemia', 'feat_cholesterol', 'feat_obesity',
    'feat_mental_health', 'feat_arthritis', 'feat_cancer', 'feat_stroke',
    'med_insulin', 'med_metformin', 'med_aspirin', 'med_statin',
    'med_beta_blocker', 'med_ace_inhibitor', 'med_diuretic', 'med_anticoagulant',
    'vit_sys_bp', 'vit_dia_bp', 'vit_heart_rate', 'vit_bmi',
    'vit_respiratory_rate', 'vit_cholesterol_total', 'vit_glucose'
]

# 3. Créer un faux patient (DataFrame avec les bonnes colonnes)
# On met des valeurs aléatoires entre 0 et 1 pour tester
fake_data = pd.DataFrame(np.random.rand(1, len(features)), columns=features)

# Pour les colonnes 'feat_' et 'med_', on met des 0 ou 1 (binaire) pour faire plus réaliste
binary_cols = [col for col in features if 'feat_' in col or 'med_' in col or 'gender' in col or 'race' in col]
for col in binary_cols:
    fake_data[col] = np.random.randint(0, 2, 1)

# On met un âge réaliste (ex: 65 ans)
fake_data['age'] = 65

print("\n😷 Données du patient simulé :")
print(fake_data.iloc[0].to_dict())

# 4. Conversion en DMatrix (XGBoost va lire les noms de colonnes ici)
dmatrix = xgb.DMatrix(fake_data)

# 5. Prédiction
probability = model.predict(dmatrix)[0]

print(f"\n🔮 Résultat de la prédiction :")
print(f"   Score de risque : {probability:.4f} ({probability*100:.2f}%)")

if probability > 0.5:
    print("⚠️ ALERTE : Risque élevé de réadmission !")
else:
    print("✅ Risque faible.")