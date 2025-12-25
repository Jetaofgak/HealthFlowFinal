import optuna
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
import xgboost as xgb
from sklearn.metrics import roc_curve, auc
from utils.data_loader import load_and_preprocess_data, get_train_val_test_splits

def get_best_params(study_name, storage="sqlite:///optuna_studies.db"):
    """
    Retrieves the best parameters from a study, preferring trials with 
    low overfitting gap (< 0.07) if available.
    """
    try:
        study = optuna.load_study(study_name=study_name, storage=storage)
    except KeyError:
        print(f"⚠️  Study {study_name} not found.")
        return None

    best_trials = study.best_trials
    # Sort by Val F1 descending (Index 1 is Val F1)
    best_trials.sort(key=lambda t: t.values[1], reverse=True)

    selected_trial = None
    for trial in best_trials:
        train_f1 = trial.values[0]
        val_f1 = trial.values[1]
        gap = abs(train_f1 - val_f1)

        if gap < 0.07:
            selected_trial = trial
            break

    # If no low-gap model found, take the top balanced one
    if not selected_trial and best_trials:
        selected_trial = best_trials[0]

    if selected_trial:
        print(f"✅ Found best trial for {study_name}: Trial #{selected_trial.number}")
        print(f"   Val F1: {selected_trial.values[1]:.4f}, Gap: {abs(selected_trial.values[0] - selected_trial.values[1]):.4f}")
        return selected_trial.params
    
    return None

def main():
    # 1. Load Data
    print("⏳ Loading data...")
    # Sklearn data (Imputed)
    df_sk, _ = load_and_preprocess_data(impute_missing=True)
    X_tr_sk, X_vl_sk, _, y_tr_sk, y_vl_sk, _ = get_train_val_test_splits(df_sk)

    # XGBoost data (Native NaNs)
    df_xgb, _ = load_and_preprocess_data(impute_missing=False)
    X_tr_xgb, X_vl_xgb, _, y_tr_xgb, y_vl_xgb, _ = get_train_val_test_splits(df_xgb)

    models_config = [
        ("RandomForest", RandomForestClassifier, False), # Name, Class, IsXGBoost
        ("AdaBoost", AdaBoostClassifier, False),
        ("DecisionTree", DecisionTreeClassifier, False),
        ("XGBoost", xgb.XGBClassifier, True)
    ]

    # Create 2x2 subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    axes = axes.flatten()

    for idx, (name, ModelClass, is_xgb) in enumerate(models_config):
        ax = axes[idx]
        study_name = f"{name}_train_val_f1_optimization"
        best_params = get_best_params(study_name)

        if not best_params:
            ax.text(0.5, 0.5, "No Params Found", ha='center', va='center')
            continue

        print(f"⚙️  Training {name} with best params...")
        
        # Select data
        if is_xgb:
            X_train, y_train = X_tr_xgb, y_tr_xgb
            X_val, y_val = X_vl_xgb, y_vl_xgb
            model = ModelClass(**best_params, random_state=42, n_jobs=-1, device="cpu")
        else:
            X_train, y_train = X_tr_sk, y_tr_sk
            X_val, y_val = X_vl_sk, y_vl_sk
            if name == "RandomForest":
                model = ModelClass(**best_params, random_state=42, n_jobs=-1)
            else:
                model = ModelClass(**best_params, random_state=42)

        model.fit(X_train, y_train)

        # Predict Probabilities
        y_prob = model.predict_proba(X_val)[:, 1]

        # Compute ROC
        fpr, tpr, _ = roc_curve(y_val, y_prob)
        roc_auc = auc(fpr, tpr)

        # Plot on specific subplot
        ax.plot(fpr, tpr, lw=2, label=f'{name} (AUC = {roc_auc:.4f})', color='darkorange')
        ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title(f'{name} ROC Curve')
        ax.legend(loc="lower right")
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    output_file = "roc_comparison_subplots.png"
    plt.savefig(output_file, dpi=300)
    print(f"\n✨ ROC Curve subplots saved to {output_file}")

if __name__ == "__main__":
    main()
