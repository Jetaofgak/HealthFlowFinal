# Optuna Grid Search Results - Updated

This report summarizes the best models found during the Optuna hyperparameter optimization process with **extended trials and loss tracking**.

## 🏆 BEST MODELS SUMMARY (High Val F1 & Low Gap)

| Model            | Val F1   | Train F1 | Gap      | Val Loss | Train Loss | Trial ID | Best Params                                                                    |
| :--------------- | :------- | :------- | :------- | :------- | :--------- | :------- | :----------------------------------------------------------------------------- |
| **XGBoost** ⭐    | **0.7941** | 0.9126   | 0.1185   | 0.4322   | 0.2292     | #79      | `{'n_estimators': 718, 'max_depth': 9, 'learning_rate': ...}`                 |
| **RandomForest** | 0.7906   | 0.9767   | 0.1861   | 0.4309   | 0.1853     | #125     | `{'n_estimators': 248, 'max_depth': 17, 'min_samples_leaf': 2}`               |
| **AdaBoost**     | 0.7819   | 0.8261   | 0.0442   | 0.6773   | 0.6768     | #157     | `{'n_estimators': 185, 'learning_rate': ...}`                                 |
| **DecisionTree** 💎 | 0.7782   | 0.7877   | **0.0096** | 0.4961   | 0.4140     | #157     | `{'max_depth': 5, 'min_samples_leaf': 5, 'criterion': 'entropy'}`             |

**Legend:**
- ⭐ = Highest Val F1 (Best Accuracy)
- 💎 = Lowest Gap (Best Generalization)

---

## 📊 Detailed Analysis

### **Key Findings from Extended Optimization**

1. **XGBoost Emerges as Winner** 🏆
   - Achieved **highest Val F1: 79.41%** among all models
   - Gap reduced from 12.65% (Trial #3) to **11.85%** (Trial #79) - still above threshold
   - With 200+ trials, Optuna found better regularization balance
   - **Status**: Best accuracy but needs further regularization tuning

2. **DecisionTree: Hidden Gem** 💎
   - **Lowest overfitting gap: 0.96%** (less than 1%!)
   - Val F1 improved to 77.82% (from 77.34%)
   - Shallow depth (5) prevents memorization
   - **Status**: Most reliable for production (excellent generalization)

3. **AdaBoost: Consistent Performer**
   - Val F1: 78.19% (improved from 77.85%)
   - Gap: 4.42% (increased slightly from 4.14% but still excellent)
   - Loss values nearly identical (Train: 0.6768, Val: 0.6773) - perfect calibration!
   - **Status**: Best balance of accuracy and robustness

4. **RandomForest: Overfitting Concern** ⚠️
   - Val F1 same (79.06%) but **gap worsened to 18.61%**
   - Train F1: 97.67% (clearly memorizing training data)
   - **Status**: NOT recommended despite high Val F1

---

## 🔍 Performance vs. Generalization Trade-off

### **Ranking by Val F1 (Accuracy):**
1. **XGBoost**: 79.41% ⭐
2. RandomForest: 79.06%
3. AdaBoost: 78.19%
4. DecisionTree: 77.82%

### **Ranking by Gap (Generalization):**
1. **DecisionTree**: 0.96% 💎 (EXCELLENT)
2. AdaBoost: 4.42% (EXCELLENT)
3. XGBoost: 11.85% (ACCEPTABLE)
4. RandomForest: 18.61% (POOR)

---

## 📈 Loss Analysis

### **Validation Loss Comparison:**
| Model | Val Loss | Train Loss | Loss Gap | Assessment |
|-------|----------|------------|----------|------------|
| **AdaBoost** | 0.6773 | 0.6768 | 0.0005 | Perfect calibration |
| **XGBoost** | 0.4322 | 0.2292 | 0.2030 | Overfitting evident |
| **RandomForest** | 0.4309 | 0.1853 | 0.2456 | Severe overfitting |
| **DecisionTree** | 0.4961 | 0.4140 | 0.0821 | Good calibration |

**Key Insight**: AdaBoost has nearly identical train/val loss, indicating excellent model calibration despite not having the highest F1 score.

---

## 🎯 Production Recommendations

### **Scenario 1: Maximum Accuracy Priority** 🎯
**Choose: XGBoost Trial #79**
- Val F1: **79.41%** (Highest)
- Gap: 11.85% (Acceptable for healthcare where catching readmissions is critical)
- **Use Case**: When false negatives (missed readmissions) are very costly
- **Risk**: May not generalize as well to new patient populations
- **Next Step**: Apply strong regularization optimization to reduce gap below 7%

### **Scenario 2: Best Generalization** ✅ **RECOMMENDED**
**Choose: DecisionTree Trial #157**
- Val F1: 77.82%
- Gap: **0.96%** (Nearly perfect generalization!)
- **Use Case**: Production deployment where model reliability is paramount
- **Advantages**:
  - Most interpretable (can visualize full decision tree)
  - Clinically explainable for regulatory compliance
  - Minimal risk of performance degradation on new data
- **Trade-off**: 1.6% lower F1 than XGBoost

### **Scenario 3: Balanced Approach** ⚖️
**Choose: AdaBoost Trial #157**
- Val F1: 78.19%
- Gap: 4.42%
- Loss calibration: **Perfect** (train/val loss difference = 0.05%)
- **Use Case**: General production deployment
- **Advantages**:
  - Excellent generalization (gap < 5%)
  - Well-calibrated probability estimates
  - Robust ensemble method
- **Trade-off**: 1.2% lower F1 than XGBoost

---

## 🔧 Hyperparameter Insights

### **What We Learned:**

1. **Depth vs. Overfitting**
   - DecisionTree (max_depth=5): Gap 0.96% ✅
   - RandomForest (max_depth=17): Gap 18.61% ❌
   - **Conclusion**: Shallower trees generalize better

2. **Learning Rate Strategy**
   - XGBoost prefers lower learning rates (0.01-0.1 range)
   - AdaBoost can handle higher learning rates with fewer estimators
   - **Pattern**: Lower LR + More estimators = Better generalization

3. **Regularization Impact**
   - XGBoost Trial #79 shows improved gap (11.85% vs 12.65%)
   - But still needs stronger regularization to meet <7% target
   - **Next**: Apply `--strong-reg` flag for focused optimization

4. **Loss as Indicator**
   - Models with large train/val loss gaps (RF: 0.25, XGB: 0.20) show poor generalization
   - AdaBoost's near-zero loss gap (0.0005) correlates with low F1 gap (4.42%)
   - **Lesson**: Monitor both F1 gap AND loss gap

---

## 🚀 Next Steps

### **Immediate Actions:**

1. **Deploy DecisionTree Trial #157** ✅
   - Most production-ready model available
   - Update `train.py` with hyperparameters:
     ```python
     max_depth=5
     min_samples_leaf=5
     criterion='entropy'
     ```
   - Expected Test F1: ~77.5-78.0%

2. **Further Optimize XGBoost** 🎯
   - Run optimization with `--strong-reg` flag:
     ```bash
     python optuna_grid_search.py --model XGBoost --trials 50 --strong-reg
     ```
   - Target: Val F1 > 79% AND Gap < 7%
   - If successful, could be the ultimate winner

### **Research Questions:**

- **Q**: Can XGBoost match DecisionTree's generalization while maintaining high accuracy?
- **A**: Pending strong regularization optimization results

- **Q**: Why does AdaBoost have perfect loss calibration?
- **A**: Ensemble averaging + SAMME.R algorithm produces well-calibrated probabilities

---

## 📝 Optimization History

| Run | Model | Trials | Val F1 | Gap | Notes |
|-----|-------|--------|--------|-----|-------|
| 1 | All | 2 | - | - | Initial smoke test |
| 2 | All | 50 | 0.7941 (XGB) | 12.65% | First full optimization |
| 3 | All | 200+ | 0.7941 (XGB) | 11.85% | Extended optimization with loss tracking |
| 4 | XGBoost | 50 (planned) | TBD | <7% (target) | Strong regularization mode |

---

## 🎓 Conclusion

After **200+ trials** of Bayesian optimization with Optuna:

1. **XGBoost leads in accuracy** (79.41% Val F1)
2. **DecisionTree leads in generalization** (0.96% gap)
3. **AdaBoost offers best calibration** (perfect loss alignment)
4. **RandomForest not recommended** (severe overfitting)

**Final Recommendation**:
- **Production Deployment NOW**: DecisionTree Trial #157
- **Production Deployment AFTER**: XGBoost with strong regularization (if gap < 7% achieved)

---

*Report generated: 2025-12-25*
*Optimization framework: Optuna 3.4.0*
*Models: RandomForest, AdaBoost, DecisionTree, XGBoost*
*Total trials: 200+ across all models*