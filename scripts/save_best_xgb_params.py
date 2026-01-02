import optuna
import sys
import json

try:
    study = optuna.load_study(
        study_name='XGBoost_train_val_f1_optimization', 
        storage='sqlite:///optuna_studies.db'
    )
    
    best_trials = study.best_trials
    best_trials.sort(key=lambda t: t.values[1], reverse=True) 
    
    selected_trial = None
    for trial in best_trials:
        train_f1 = trial.values[0]
        val_f1 = trial.values[1]
        gap = abs(train_f1 - val_f1)
        if gap < 0.07:
            selected_trial = trial
            break
            
    if not selected_trial and best_trials:
        selected_trial = best_trials[0]
        
    with open('best_params.txt', 'w') as f:
        json.dump(selected_trial.params, f, indent=4)
        
    print("Saved to best_params.txt")

except Exception as e:
    print(f"Error: {e}")
