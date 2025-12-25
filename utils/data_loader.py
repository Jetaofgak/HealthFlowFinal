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
