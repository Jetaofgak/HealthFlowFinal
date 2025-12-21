import os
import pandas as pd
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

if __name__ == "__main__":
    monitor = FairnessMonitor()
    # Test connection
    try:
        df = monitor.fetch_data()
        print(f"Fetched {len(df)} rows")
    except Exception as e:
        print(f"Connection failed: {e}")
