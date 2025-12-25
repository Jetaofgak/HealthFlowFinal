# Optuna Grid Search Results

This report summarizes the best models found during the Optuna hyperparameter optimization process.

## 🏆 BEST MODELS SUMMARY (High Val F1 & Low Gap)

| Model            | Val F1 | Train F1 | Gap    | Trial ID | Best Params                                                                    |
| :--------------- | :----- | :------- | :----- | :------- | :----------------------------------------------------------------------------- |
| **RandomForest** | 0.7906 | 0.8946   | 0.1039 | #21      | `{'n_estimators': 284, 'max_depth': 16, 'min_samples_leaf': 2}`                |
| **AdaBoost**     | 0.7785 | 0.8199   | 0.0414 | #37      | `{'n_estimators': 162, 'learning_rate': 0.872660528}`                          |
| **DecisionTree** | 0.7734 | 0.7881   | 0.0147 | #24      | `{'max_depth': 5, 'min_samples_leaf': 3, 'criterion': 'entropy'}`              |
| **XGBoost**      | 0.7855 | 0.9120   | 0.1265 | #3       | `{'n_estimators': 859, 'max_depth': 4, 'learning_rate': 0.027668630048128495}` |

## Analysis

- **RandomForest** achieved the highest Validation F1 (0.7906) but has a moderate overfitting gap (10.39%).
- **AdaBoost** offers a very balanced performance with Val F1 of 0.7785 and a low gap of 4.14%.
- **DecisionTree** has the lowest gap (1.47%) but slightly lower F1 Score, indicating strong generalization but potentially underfitting compared to ensemble methods.
- **XGBoost** performed well (Val F1: 0.7855) but showed a higher gap (12.65%) in this specific trial run compared to previous shorter runs.

> **Note**: These results are based on a 50-trial optimization run.
