import joblib
import xgboost as xgb
import pandas as pd
import numpy as np

# 1. Charger le pack
print("📂 Chargement du modèle...")
pack = joblib.load("xgboost_readmission_pack_100k.joblib")
model = pack["model"]
features = pack["features"]

# 2. Générer un patient ALÉATOIRE MAIS RÉALISTE
# On crée un dictionnaire vide
fake_patient = {}

for col in features:
    if "feat_" in col or "med_" in col or "gender" in col or "race" in col:
        # Pour les maladies/médicaments : Soit 0, soit 1
        fake_patient[col] = np.random.randint(0, 2)
    elif "age" in col:
        # Âge entre 20 et 90 ans
        fake_patient[col] = np.random.randint(20, 90)
    elif "vit_" in col:
        # Constantes vitales (on met des valeurs moyennes + un peu de bruit)
        fake_patient[col] = np.random.normal(100, 20) # Valeur bidon juste pour que ça varie
    else:
        fake_patient[col] = 0

# 3. Créer le DataFrame
df = pd.DataFrame([fake_patient])

# Important : On s'assure que les colonnes sont dans le bon ordre !
df = df[features]

# 4. Conversion et Prédiction
dmatrix = xgb.DMatrix(df)
prob = model.predict(dmatrix)[0]

print(f"\n👤 Patient généré : {fake_patient['age']} ans, Diabète={fake_patient['feat_diabetes']}")
print(f"🔮 Risque calculé : {prob:.2%} (Change à chaque lancement !)")