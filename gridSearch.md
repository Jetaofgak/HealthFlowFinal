# Optuna Grid Search Results

This report summarizes the best models found during the Optuna hyperparameter optimization process.

## 🏆 BEST MODELS SUMMARY (High Val F1 & Low Gap)

| Model            | Val F1 | Train F1 | Gap    | Val Loss | Train Loss | Trial ID | Best Params                                                                    |
| :--------------- | :----- | :------- | :----- | :------- | :--------- | :------- | :----------------------------------------------------------------------------- |
| **RandomForest** | 0.7906 | 0.8946   | 0.1039 | 0.4376   | 0.2792     | #21      | `{'n_estimators': 284, 'max_depth': 16, 'min_samples_leaf': 2}`                |
| **AdaBoost**     | 0.7785 | 0.8199   | 0.0414 | 0.6748   | 0.6746     | #37      | `{'n_estimators': 162, 'learning_rate': 0.872660528}`                          |
| **DecisionTree** | 0.7734 | 0.7881   | 0.0147 | 0.5978   | 0.4150     | #24      | `{'max_depth': 5, 'min_samples_leaf': 3, 'criterion': 'entropy'}`              |
| **XGBoost**      | 0.7855 | 0.9120   | 0.1265 | 0.4411   | 0.2275     | #3       | `{'n_estimators': 859, 'max_depth': 4, 'learning_rate': 0.027668630048128495}` |

## Detailed Analysis

### 1. Performance vs. Generalization Trade-off

The optimization results highlight a classic trade-off between pure performance (Validation F1) and generalization (Overfitting Gap).

- **RandomForest (Trial #21)**:

  - **Pros**: Top performer with **F1: 79.1%**.
  - **Cons**: Significant overfitting gap (~10.4%). The large depth (`max_depth=16`) contributed to memorizing training data (Train F1: ~89.5%).
  - **Recommendation**: Good candidate if maximum accuracy is the only goal and slight overfitting is acceptable.

- **AdaBoost (Trial #37)**:

  - **Pros**: Excellent balance. F1: 77.9% with a very low gap of **4.1%**.
  - **Cons**: Slightly lower peak performance than RF/XGB.
  - **Recommendation**: **Best "Safe" Choice**. Highly robust and unlikely to degrade on unseen test data.

- **XGBoost (Trial #3)**:

  - **Pros**: Competitive F1 (78.6%) and extremely high training score (91.2%), showing high capacity.
  - **Cons**: Highest overfitting gap (~12.7%) in this specific run.
  - **Context**: In previous shorter runs, we found configurations with gaps < 5%. This specific trial prioritized F1 too aggressively.
  - **Adjustment**: Increasing `reg_lambda` or reducing `max_depth` (currently 4) further could tame this.

- **DecisionTree (Trial #24)**:
  - **Pros**: Lowest overfitting (1.5% gap).
  - **Cons**: Lowest F1 score (~77.3%).
  - **Recommendation**: Useful baseline, but ensemble methods (RF, Boosting) are clearly superior here.

## 🚀 Final Recommendation

For the **HealthFlow** production pipeline, we have two strong options:

1.  **Conservative / Robust**: **AdaBoost** (Trial #37). It provides stable, predictable performance with minimal risk of overfitting.
2.  **Aggressive / High-Performance**: **XGBoost**. Although Trial #3 overfitted, previous runs showed it can match RF's performance with better generalization when properly regularized.

**Action Taken**: We initially selected a balanced **XGBoost** configuration (from a previous run with **F1: 79.0% / Gap: 4.9%**) for `train.py` to get the best of both worlds.

## 🔧 Hyperparameter Insights

- **Depth Matters**: Deeper trees (`max_depth=16` in RF) directly correlated with higher overfitting gaps (>10%).
- **Learning Rate**: AdaBoost favored a high learning rate (~0.87), while XGBoost preferred lower ones (~0.02) combined with more estimators.
- **Regularization**: The best XGBoost models consistently utilized L2 regularization (`reg_lambda` > 3) to control model complexity.
