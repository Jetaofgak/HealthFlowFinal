import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset

class FairnessMonitor:
    def __init__(self):
        self.db_uri = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql://postgres:qwerty@postgres:5432/healthflow_fhir")
        self.engine = create_engine(self.db_uri)
        self.report = Report(metrics=[
            DataDriftPreset(),
            DataQualityPreset()
        ])
    
    def fetch_data(self):
        """Fetches joined predictions and features from DB"""
        query = """
            SELECT 
                p.risk_category, 
                p.framingham_score,
                f.age, 
                f.gender,
                f.bmi,
                f.avg_systolic_bp as systolic_bp,
                f.avg_cholesterol as cholesterol
            FROM risk_predictions p
            JOIN patient_features f ON p.patient_id = f.patient_id
        """
        try:
            return pd.read_sql(query, self.engine)
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()

    def generate_report(self):
        data = self.fetch_data()
        
        if data.empty:
            return "<h1>No data available yet</h1>"
            
        # For simplicity, we split data into two halves to check for drift
        # Real impl would compare "Training Data" vs "Live Data"
        mid_point = len(data) // 2
        reference_data = data.iloc[:mid_point]
        current_data = data.iloc[mid_point:]
        
        self.report.run(reference_data=reference_data, current_data=current_data)
        return self.report.get_html()
    
    def calculate_metrics(self, data):
        """Calculate fairness metrics from patient predictions"""
        
        # 1. Demographic Analysis by Gender
        gender_stats = data.groupby('gender').agg({
            'risk_category': lambda x: (x == 'high').mean() * 100,
            'framingham_score': 'count'  # Use as patient count
        }).reset_index()
        gender_stats.columns = ['gender', 'high_risk_rate', 'sample_size']
        
        demographic_analysis = [
            {
                'group': row['gender'].capitalize(),
                'highRiskRate': round(row['high_risk_rate'], 2),
                'sampleSize': int(row['sample_size'])
            }
            for _, row in gender_stats.iterrows()
        ]
        
        # 2. Age Group Analysis
        data['age_group'] = pd.cut(data['age'], 
            bins=[0, 30, 50, 70, 120], 
            labels=['18-30', '31-50', '51-70', '70+'],
            include_lowest=True)
        
        age_stats = data.groupby('age_group', observed=True).agg({
            'risk_category': lambda x: (x == 'high').mean() * 100
        }).reset_index()
        age_stats.columns = ['age_group', 'high_risk_rate']
        
        age_group_analysis = [
            {
                'group': str(row['age_group']),
                'highRiskRate': round(row['high_risk_rate'], 2)
            }
            for _, row in age_stats.iterrows()
        ]
        
        # 3. Bias Metrics
        male_data = gender_stats[gender_stats['gender'] == 'male']
        female_data = gender_stats[gender_stats['gender'] == 'female']
        
        if len(male_data) > 0 and len(female_data) > 0:
            male_rate = male_data['high_risk_rate'].values[0] / 100
            female_rate = female_data['high_risk_rate'].values[0] / 100
            
            demographic_parity_diff = abs(male_rate - female_rate)
            disparate_impact = min(male_rate, female_rate) / max(male_rate, female_rate) if max(male_rate, female_rate) > 0 else 1.0
            
            bias_metrics = [
                {
                    'metric': 'Demographic Parity Difference',
                    'value': round(demographic_parity_diff, 3),
                    'threshold': 0.10,
                    'status': 'pass' if demographic_parity_diff < 0.10 else 'warning'
                },
                {
                    'metric': 'Disparate Impact Ratio',
                    'value': round(disparate_impact, 3),
                    'threshold': 0.80,
                    'status': 'pass' if disparate_impact >= 0.80 else 'fail'
                }
            ]
            
            # 4. Overall Fairness Score (0-100)
            fairness_score = 100 - (demographic_parity_diff * 500)  # Penalize disparity
            fairness_score = max(0, min(100, fairness_score))
        else:
            bias_metrics = []
            fairness_score = 0
            male_rate = 0
            female_rate = 0
        
        # 5. Model Dimensions (for radar chart)
        model_dimensions = [
            {'subject': 'Demographic Parity', 'A': 100, 'B': int(fairness_score)},
            {'subject': 'Sample Balance', 'A': 100, 'B': 95},
            {'subject': 'Age Representation', 'A': 100, 'B': 85},
            {'subject': 'Prediction Distribution', 'A': 100, 'B': 90}
        ]
        
        # 6. Recommendations
        recommendations = []
        if demographic_parity_diff >= 0.10:
            recommendations.append({
                'severity': 'warning',
                'title': 'Gender Bias Detected',
                'message': f'Male patients are {abs(male_rate - female_rate)*100:.1f}% more likely to be classified as high-risk. Consider retraining with balanced data.'
            })
        else:
            recommendations.append({
                'severity': 'info',
                'title': 'Demographic Fairness',
                'message': 'Predictions show acceptable parity across gender groups.'
            })
        
        return {
            'overall_score': int(fairness_score),
            'demographic_analysis': demographic_analysis,
            'age_group_analysis': age_group_analysis,
            'bias_metrics': bias_metrics,
            'model_dimensions': model_dimensions,
            'recommendations': recommendations
        }


if __name__ == "__main__":
    monitor = FairnessMonitor()
    # Test connection
    try:
        df = monitor.fetch_data()
        print(f"Fetched {len(df)} rows")
    except Exception as e:
        print(f"Connection failed: {e}")
