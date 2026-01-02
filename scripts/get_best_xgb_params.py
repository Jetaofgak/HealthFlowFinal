import optuna
import sys

try:
    study = optuna.load_study(
        study_name='XGBoost_train_val_f1_optimization', 
        storage='sqlite:///optuna_studies.db'
    )
    
    # Get best trial based on the optimization direction (maximize val f1)
    # Note: earlier we saw the script uses [max, max], so best_trials returns a list of Pareto optimal solutions.
    # We need to pick one. The previous script logic picked based on gap < 0.07.
    
    best_trials = study.best_trials
    best_trials.sort(key=lambda t: t.values[1], reverse=True) # Sort by Val F1 desc
    
    selected_trial = None
    for trial in best_trials:
        train_f1 = trial.values[0]
        val_f1 = trial.values[1]
        gap = abs(train_f1 - val_f1)
        if gap < 0.07:
            selected_trial = trial
            break
            
    if not selected_trial and best_trials:
        selected_trial = best_trials[0] # Fallback to best F1
        
    print("SELECTED_PARAMS_START")
    print(selected_trial.params)
    print("SELECTED_PARAMS_END")

except Exception as e:
    print(f"Error: {e}")
