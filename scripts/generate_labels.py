#!/usr/bin/env python3
"""
Generate synthetic readmission labels for Synthea patients
Based on risk factors: age, conditions, medications, vitals
"""

import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv('dataset_119_patients_with_nlp.csv')

print(f"📊 Loaded {len(df)} patients")

# Generate readmission risk score (0-1)
risk_score = np.zeros(len(df))

# Age risk (older = higher risk)
risk_score += (df['age'] / 100) * 0.2

# Condition risk
risk_score += df['cond_diabetes'] * 0.15
risk_score += df['cond_hypertension'] * 0.1
risk_score += df['cond_chf'] * 0.2
risk_score += df['cond_copd'] * 0.15
risk_score += df['cond_ckd'] * 0.15

# Polypharmacy risk
risk_score += df['polypharmacy'] * 0.1

# NLP-derived risk
risk_score += (df['nlp_num_conditions'] / 10) * 0.1
risk_score += df['nlp_polypharmacy'] * 0.05

# Normalize to 0-1
risk_score = np.clip(risk_score, 0, 1)

# Generate binary labels (threshold at 0.4 for ~40% readmission rate)
df['label_readmission'] = (risk_score > 0.4).astype(int)

# Add risk score for reference
df['risk_score'] = risk_score

print(f"\n📊 Label Distribution:")
print(df['label_readmission'].value_counts())
print(f"\nBalance: {df['label_readmission'].value_counts(normalize=True)}")

# Save
df.to_csv('dataset_119_patients_with_nlp.csv', index=False)

print(f"\n✅ Labels generated and saved!")
print(f"   Readmission rate: {df['label_readmission'].mean():.1%}")
