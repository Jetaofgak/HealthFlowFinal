# Optuna Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: use executing-plans skill to implement this plan task-by-task.

**Goal:** Integrate Optuna for hyperparameter optimization of Random Forest, AdaBoost, Decision Tree, and XGBoost models. The goal is to maximize the F1 score while minimizing overfitting (low difference between Train and Validation F1).

**Architecture:**

1.  **Shared Utility:** `utils/data_loader.py` with conditional imputation (impute for sklearn, keep NaNs for XGBoost).
2.  **Configurations:** Root-level `requirements.txt`.
3.  **Optimization Script:** `optuna_grid_search.py` with multi-objective optimization and extended XGBoost search space.

**Tech Stack:** Python, Optuna, Scikit-learn, Pandas, XGBoost, SQLite.

---

### Task 1: Setup Environment & Dependencies

**Files:**

- Create: `requirements.txt` (Root)

**Step 1: Create requirements.txt**

Create a root-level `requirements.txt` with all necessary ML dependencies:

```text
pandas==2.1.4
numpy==1.26.2
scikit-learn==1.3.2
xgboost==2.0.3
optuna==3.4.0
optuna-dashboard==0.14.0
matplotlib
seaborn
```

**Step 2: Install dependencies**

```bash
pip install -r requirements.txt
```

---

### Task 2: Shared Data Loader

**Files:**

- Create: `utils/data_loader.py`
- Create: `utils/__init__.py`

**Step 1: Implement data loader with conditional imputation**

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os

CSV_PATH = "dataset_with_nlp.csv"
TARGET_COL = 'label_readmission'

def load_and_preprocess_data(csv_path=CSV_PATH, target_col=TARGET_COL, impute_missing=True):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"❌ File not found: {csv_path}")

    print(f"📂 Loading {csv_path} (impute_missing={impute_missing})...")
    df = pd.read_csv(csv_path)

    # 1. Drop high null columns (>80%)
    null_threshold = 0.8
    null_counts = df.isnull().mean()
    drop_cols = null_counts[null_counts > null_threshold].index
    df = df.drop(columns=drop_cols)

    # 2. Drop identifiers & constant columns
    ids = ['encounter_id', 'patient_id', 'start_date']
    df = df.drop(columns=[c for c in ids if c in df.columns])

    # 3. Handle Categoricals
    le_dict = {}
    for col in df.select_dtypes(include=['object']).columns:
        if col != target_col:
            df[col] = df[col].astype(str)
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            le_dict[col] = le

    # 4. Conditional Imputation
    if impute_missing:
        # For sklearn models that can't handle NaN
        df = df.fillna(df.median(numeric_only=True))
    # else: XGBoost handles NaNs natively

    return df, le_dict

def get_train_val_test_splits(df, target_col=TARGET_COL, test_size=0.2, val_size=0.25, random_state=42):
    """
    Splits: 60% Train, 20% Val, 20% Test
    """
    X = df.drop(columns=[target_col])
    y = df[target_col]

    # First split: Train+Val vs Test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Second split: Train vs Val
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_size, random_state=random_state, stratify=y_temp
    )

    return X_train, X_val, X_test, y_train, y_val, y_test
```

**Step 2: Verify Import**

- Create `utils/__init__.py`.

---

### Task 3: Refactor Train Script

**Files:**

- Modify: `train.py`

**Step 1: Use shared loader**

- Replace data loading/preprocessing block with:

```python
from utils.data_loader import load_and_preprocess_data, get_train_val_test_splits

# ...
# XGBoost handles NaNs, so impute_missing=False
df, _ = load_and_preprocess_data(CSV_PATH, TARGET_COL, impute_missing=False)
X_train, X_val, X_test, y_train, y_val, y_test = get_train_val_test_splits(df, TARGET_COL)
# ...
```

---

### Task 4: Optuna Grid Search Script

**Files:**

- Create: `optuna_grid_search.py`

**Step 1: Implement Script with Dual Data Loading & Extended XGBoost Params**

```python
import argparse
import optuna
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
import xgboost as xgb
from sklearn.metrics import f1_score
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
        model = xgb.XGBClassifier(**params, random_state=42, n_jobs=-1, device="cpu")

    model.fit(X_train, y_train)

    y_train_pred = model.predict(X_train)
    y_val_pred = model.predict(X_val)

    train_f1 = f1_score(y_train, y_train_pred)
    val_f1 = f1_score(y_val, y_val_pred)

    gap = abs(train_f1 - val_f1)

    return val_f1, gap

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

    for model_name in models:
        study_name = f"{model_name}_f1_gap_optimization"
        storage = "sqlite:///optuna_studies.db"

        study = optuna.create_study(
            study_name=study_name,
            storage=storage,
            load_if_exists=True,
            directions=["maximize", "minimize"]
        )

        print(f"🚀 Starting optimization for {model_name}...")
        study.optimize(lambda t: objective(t, model_name, data_pack), n_trials=args.trials)
        print(f"✅ {model_name} finished.")

    print("\n✨ All studies complete. Run: optuna-dashboard sqlite:///optuna_studies.db")
```

---

### Task 5: Verification & Selection

**Step 1: Smoke Test**

```bash
python optuna_grid_search.py --trials 2
```

**Step 2: Dashboard Analysis**

```bash
optuna-dashboard sqlite:///optuna_studies.db
```

- Open dashboard.
- For each model, check "Pareto Front".
- **Selection Criteria**:
  - Priority 1: High Validation F1 (>0.75) with Gap < 0.05.
  - Priority 2: Best F1 balance if no low-gap solution exists.

---

### Task 6: Retrain Best Model (Manual Step)

**Step 1**: Extract best hyperparameters from dashboard.
**Step 2**: Update `train.py` or new script with these params.
**Step 3**: Retrain on full Train+Val and evaluate on Test set.
