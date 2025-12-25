import optuna
import pandas as pd
import matplotlib.pyplot as plt
import os
from optuna.visualization import plot_optimization_history, plot_param_importances

def generate_report(storage="sqlite:///optuna_studies.db", output_file="OPTIMIZATION_REPORT.md"):
    print(f"Loading studies from {storage}...")
    
    try:
        # Get all study summaries
        summaries = optuna.study.get_all_study_summaries(storage=storage)
    except Exception as e:
        print(f"❌ Failed to load storage: {e}")
        return

    report_content = "# Optuna Optimization Report\n\n"
    report_content += "This report summarizes the best hyperparameters and performance metrics for each model optimized using Optuna.\n\n"

    # Create images directory if not exists
    os.makedirs("ml_optimization/reporting/images", exist_ok=True)

    for summary in summaries:
        study_name = summary.study_name
        study = optuna.load_study(study_name=study_name, storage=storage)
        
        print(f"Processing study: {study_name}...")
        
        report_content += f"## Study: {study_name}\n\n"
        
        # Best Trials Logic (Pareto Front for Multi-objective)
        best_trials = study.best_trials
        # Sort by Val F1 (2nd objective)
        best_trials.sort(key=lambda t: t.values[1], reverse=True)
        
        # Pick best consistent trial (low gap)
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
            
        if selected_trial:
            val_f1 = selected_trial.values[1]
            train_f1 = selected_trial.values[0]
            gap = abs(train_f1 - val_f1)
            
            report_content += "### 🏆 Best Consistent Trial\n"
            report_content += f"- **Trial ID**: #{selected_trial.number}\n"
            report_content += f"- **Validation F1**: {val_f1:.4f}\n"
            report_content += f"- **Train F1**: {train_f1:.4f}\n"
            report_content += f"- **Overfitting Gap**: {gap:.4f}\n\n"
            
            report_content += "### ⚙️ Best Hyperparameters\n"
            report_content += "```json\n"
            import json
            report_content += json.dumps(selected_trial.params, indent=4)
            report_content += "\n```\n\n"
        else:
            report_content += "No successful trials found.\n\n"

        # Visualizations (Using Matplotlib backend for static images if possible, else saving html/png)
        # Optuna visualization returns plotly figures. We can't easily save them as static images without kaleido/orca.
        # So we will write a note or use matplotlib alternatives if available.
        # Since the user environment might not have kaleido, we will skip generating images for now 
        # or use simple matplotlib replacements.
        
        # Simple History Plot using Matplotlib
        try:
            df = study.trials_dataframe()
            if not df.empty and 'values_1' in df.columns: # values_1 is val_f1
                plt.figure(figsize=(10, 6))
                plt.plot(df.number, df.values_1, marker='o', linestyle='-', color='b', label='Val F1')
                plt.plot(df.number, df.values_0, marker='x', linestyle='--', color='r', label='Train F1')
                plt.xlabel('Trial')
                plt.ylabel('F1 Score')
                plt.title(f'Optimization History: {study_name}')
                plt.legend()
                plt.grid(True)
                
                img_path = f"ml_optimization/reporting/images/{study_name}_history.png"
                plt.savefig(img_path)
                plt.close()
                
                # Make path relative for markdown
                rel_path = f"ml_optimization/reporting/images/{study_name}_history.png"
                report_content += f"### 📈 Optimization History\n![History]({rel_path})\n\n"
        except Exception as e:
            print(f"Could not generate plot for {study_name}: {e}")

    with open(output_file, "w") as f:
        f.write(report_content)
    
    print(f"✅ Report generated: {output_file}")

if __name__ == "__main__":
    generate_report()
