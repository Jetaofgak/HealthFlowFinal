import os

import numpy as np
import pandas as pd
import xgboost as xgb


def load_model() -> xgb.Booster:
    """Load the UBJ model (fallback to JSON for backward compatibility)."""
    print("🔄 Chargement du modèle...")
    model = xgb.Booster()

    model_candidates = [
        "xgboost_readmission_model.ubj",
        "xgboost_readmission_model.json",
    ]

    for candidate in model_candidates:
        if os.path.exists(candidate):
            model.load_model(candidate)
            print(f"✅ Modèle chargé depuis : {candidate} !")
            return model

    raise FileNotFoundError(
        "Aucun fichier modèle (.ubj ou .json) n'a été trouvé à la racine du projet."
    )


def main():
    model = load_model()

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

    fake_data = pd.DataFrame(np.random.rand(1, len(features)), columns=features)
    binary_cols = [col for col in features if 'feat_' in col or 'med_' in col or 'gender' in col or 'race' in col]
    for col in binary_cols:
        fake_data[col] = np.random.randint(0, 2, 1)
    fake_data['age'] = 65

    print("\n😷 Données du patient simulé :")
    print(fake_data.iloc[0].to_dict())

    dmatrix = xgb.DMatrix(fake_data)
    probability = model.predict(dmatrix)[0]

    print("\n🔮 Résultat de la prédiction :")
    print(f"   Score de risque : {probability:.4f} ({probability*100:.2f}%)")

    if probability > 0.5:
        print("⚠️ ALERTE : Risque élevé de réadmission !")
    else:
        print("✅ Risque faible.")


if __name__ == "__main__":
    main()
