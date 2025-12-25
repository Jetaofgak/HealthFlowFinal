import optuna
import pandas as pd
import numpy as np
from sklearn.metrics import log_loss
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
import xgboost as xgb
from utils.data_loader import load_and_preprocess_data, get_train_val_test_splits

def get_loss_for_trial(study_name, trial_number, model_type):
    storage = "sqlite:///optuna_studies.db"
    try:
        study = optuna.load_study(study_name=study_name, storage=storage)
        trial = study.trials[trial_number]
        params = trial.params
        
        # Load Data
        if model_type == "XGBoost":
            df, _ = load_and_preprocess_data(impute_missing=False)
        else:
            df, _ = load_and_preprocess_data(impute_missing=True)
            
        X_train, X_val, X_test, y_train, y_val, y_test = get_train_val_test_splits(df)
        
        # Initialize Model
        if model_type == "RandomForest":
            model = RandomForestClassifier(**params, random_state=42, n_jobs=-1)
        elif model_type == "AdaBoost":
            model = AdaBoostClassifier(**params, random_state=42)
        elif model_type == "DecisionTree":
            model = DecisionTreeClassifier(**params, random_state=42)
        elif model_type == "XGBoost":
            model = xgb.XGBClassifier(**params, random_state=42, n_jobs=-1, device="cpu", eval_metric="logloss")

        # Train
        model.fit(X_train, y_train)
        
        # Predict Proba
        y_train_prob = model.predict_proba(X_train)
        y_val_prob = model.predict_proba(X_val)
        
        train_loss = log_loss(y_train, y_train_prob)
        val_loss = log_loss(y_val, y_val_prob)
        
        return train_loss, val_loss

    except Exception as e:
        print(f"Error for {model_type}: {e}")
        return None, None

# Updated targets from recent run
targets = [
    ("RandomForest", 21),   # Same as before
    ("AdaBoost", 37),       # Same as before
    ("DecisionTree", 81),   # NEW
    ("XGBoost", 79)         # NEW
]

print(f"{'Model':<15} | {'Val Loss':<10} | {'Train Loss':<10}")
print("-" * 45)

for model_name, trial_id in targets:
    study_name = f"{model_name}_train_val_f1_optimization"
    try:
        t_loss, v_loss = get_loss_for_trial(study_name, trial_id, model_name)
        if t_loss is not None:
            print(f"{model_name:<15} | {v_loss:.4f}     | {t_loss:.4f}")
    except:
         print(f"{model_name:<15} | Failed to load.")
