import argparse
import optuna
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
import xgboost as xgb
from sklearn.metrics import f1_score, log_loss
from utils.data_loader import load_and_preprocess_data, get_train_val_test_splits

def objective(trial, model_name, data_pack):
    # Select correct dataset based on model type
    if model_name == "XGBoost":
        X_train, y_train, X_val, y_val = data_pack['xgb']
    else:
        X_train, y_train, X_val, y_val = data_pack['sklearn']

    if model_name == "RandomForest":
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 300),
            'max_depth': trial.suggest_int('max_depth', 3, 20),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 5)
        }
        model = RandomForestClassifier(**params, random_state=42, n_jobs=-1)
        
    elif model_name == "AdaBoost":
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 300),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 1.0, log=True)
        }
        model = AdaBoostClassifier(**params, random_state=42)
        
    elif model_name == "DecisionTree":
        params = {
            'max_depth': trial.suggest_int('max_depth', 3, 20),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 5),
            'criterion': trial.suggest_categorical('criterion', ['gini', 'entropy'])
        }
        model = DecisionTreeClassifier(**params, random_state=42)
        
    elif model_name == "XGBoost":
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 2.0),
            'reg_lambda': trial.suggest_float('reg_lambda', 1.0, 10.0),
            'gamma': trial.suggest_float('gamma', 0.0, 1.0),
            'min_child_weight': trial.suggest_int('min_child_weight', 1, 10)
        }
        # Use simple CPU for compatibility, change to 'cuda' if GPU available
        model = xgb.XGBClassifier(**params, random_state=42, n_jobs=-1, device="cpu")

    model.fit(X_train, y_train)
    
    y_train_pred = model.predict(X_train)
    y_val_pred = model.predict(X_val)
    
    # Calculate Probabilities for Log Loss
    try:
        y_train_prob = model.predict_proba(X_train)
        y_val_prob = model.predict_proba(X_val)
        train_loss = log_loss(y_train, y_train_prob)
        val_loss = log_loss(y_val, y_val_prob)
        
        # Store as user attributes so we can retrieve them later
        trial.set_user_attr("train_loss", train_loss)
        trial.set_user_attr("val_loss", val_loss)
    except:
        # Some models might fail predict_proba or have issues
        trial.set_user_attr("train_loss", -1.0)
        trial.set_user_attr("val_loss", -1.0)

    train_f1 = f1_score(y_train, y_train_pred)
    val_f1 = f1_score(y_val, y_val_pred)
    
    gap = abs(train_f1 - val_f1)
    
    # We return: Maximize Train F1, Maximize Val F1
    return train_f1, val_f1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=20, help="Number of trials per model")
    args = parser.parse_args()

    # Load Data Twice
    print("⏳ Loading data for Sklearn models (Imputed)...")
    df_sk, _ = load_and_preprocess_data(impute_missing=True)
    X_tr_sk, X_vl_sk, _, y_tr_sk, y_vl_sk, _ = get_train_val_test_splits(df_sk)
    
    print("⏳ Loading data for XGBoost (Native NaNs)...")
    df_xgb, _ = load_and_preprocess_data(impute_missing=False)
    X_tr_xgb, X_vl_xgb, _, y_tr_xgb, y_vl_xgb, _ = get_train_val_test_splits(df_xgb)
    
    data_pack = {
        'sklearn': (X_tr_sk, y_tr_sk, X_vl_sk, y_vl_sk),
        'xgb': (X_tr_xgb, y_tr_xgb, X_vl_xgb, y_vl_xgb)
    }
    
    models = ["RandomForest", "AdaBoost", "DecisionTree", "XGBoost"]
    
    # Store study name -> DB URL for user convenience
    print("\nStarting optimization...")
    
    for model_name in models:
        # Changed study name to avoid conflict with previous 'gap' optimization
        study_name = f"{model_name}_train_val_f1_optimization" 
        storage = "sqlite:///optuna_studies.db"
        
        # Directions: Maximize Train F1, Maximize Val F1
        study = optuna.create_study(
            study_name=study_name, 
            storage=storage, 
            load_if_exists=True,
            directions=["maximize", "maximize"] 
        )
        
        print(f"🚀 Starting optimization for {model_name}...")
        try:
            study.optimize(lambda t: objective(t, model_name, data_pack), n_trials=args.trials)
            print(f"✅ {model_name} finished.")
        except Exception as e:
            print(f"❌ {model_name} failed: {e}")
    

    print("\n✨ All studies complete. Run: optuna-dashboard sqlite:///optuna_studies.db")
    
    print("\n🏆 BEST MODELS SUMMARY (High Val F1 & Low Gap)")
    print("="*95)
    print(f"{'Model':<15} | {'Val F1':<10} | {'Train F1':<10} | {'Gap':<10} | {'Trial ID':<8} | {'Best Params'}")
    print("-" * 95)
    
    for model_name in models:
        # Load the new study name
        study_name = f"{model_name}_train_val_f1_optimization"
        try:
            study = optuna.load_study(study_name=study_name, storage="sqlite:///optuna_studies.db")
            
            # Filter Pareto front
            best_trials = study.best_trials
            
            # Sort by Val F1 descending (Index 1 is Val F1 now)
            best_trials.sort(key=lambda t: t.values[1], reverse=True)
            
            selected_trial = None
            for trial in best_trials:
                train_f1 = trial.values[0]
                val_f1 = trial.values[1]
                gap = abs(train_f1 - val_f1)
                
                if gap < 0.07:  # Threshold for "low overfitting"
                    selected_trial = trial
                    break
            
            # If no low-gap model found, just take the top balanced one
            if not selected_trial and best_trials:
                selected_trial = best_trials[0]
                
            if selected_trial:
                train_f1 = selected_trial.values[0]
                val_f1 = selected_trial.values[1]
                gap = abs(train_f1 - val_f1)
                
                params_str = str(selected_trial.params)[:50] + "..." # Truncate for display
                print(f"{model_name:<15} | {val_f1:.4f}     | {train_f1:.4f}     | {gap:.4f}     | #{selected_trial.number:<7} | {params_str}")
            else:
                print(f"{model_name:<15} | No successful trials found.")
                
        except Exception:
            print(f"{model_name:<15} | Study not found (Run optimization first).")
            
    print("="*95)
