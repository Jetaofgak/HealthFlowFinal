from flask import Blueprint, jsonify, request
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.risk_score import RiskPrediction, Base
from models.prediction_model import CVDRiskModel
from calculators.framingham_score import FraminghamCalculator
from calculators.ascvd_calculator import ASCVDCalculator
from services.xgboost_service import XGBoostPredictionService
from config import Config
import logging

logger = logging.getLogger(__name__)

prediction_bp = Blueprint('predictions', __name__)

# Initialize XGBoost service (singleton)
xgb_service = None

def get_xgb_service():
    global xgb_service
    if xgb_service is None:
        xgb_service = XGBoostPredictionService()
    return xgb_service

# Initialisation DB
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Initialisation du modèle
cvd_model = CVDRiskModel()

@prediction_bp.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'UP',
        'service': 'ML-Predictor',
        'model_version': cvd_model.version
    })

@prediction_bp.route('/predict/<patient_id>', methods=['POST'])
def predict_risk(patient_id):
    """Prédit le risque cardiovasculaire d'un patient"""
    try:
        session = Session()
        
        # Récupérer les features du patient
        query = text("""
            SELECT 
                age, gender, bmi, 
                avg_systolic_bp, avg_diastolic_bp,
                avg_cholesterol, avg_hdl, avg_ldl, avg_triglycerides,
                features_json
            FROM patient_features
            WHERE patient_id = :patient_id
        """)
        
        result = session.execute(query, {'patient_id': patient_id}).fetchone()
        
        if not result:
            return jsonify({'error': 'Patient features not found'}), 404
        
        # Construire le dictionnaire de features
        features = {
            'age': result[0],
            'gender': result[1],
            'bmi': result[2],
            'avg_systolic_bp': result[3],
            'avg_diastolic_bp': result[4],
            'avg_cholesterol': result[5],
            'avg_hdl': result[6],
            'avg_ldl': result[7],
            'avg_triglycerides': result[8]
        }
        
        # Calculer le risque avec le modèle simple
        risk_percentage = cvd_model.predict(features)
        risk_category = cvd_model.classify_risk(risk_percentage)
        
        # Calculer le score de Framingham
        framingham_score = None
        try:
            framingham_score = FraminghamCalculator.calculate(
                age=features['age'],
                gender=features['gender'],
                total_cholesterol=features['avg_cholesterol'],
                hdl=features.get('avg_hdl', 50),
                systolic_bp=features['avg_systolic_bp'],
                on_bp_medication=False,  # À améliorer avec vraies données
                smoker=False,  # À améliorer avec vraies données
                diabetic=False  # À améliorer avec vraies données
            )
        except Exception as e:
            logger.warning(f"Framingham calculation failed: {e}")
        
        # Calculer ASCVD (si applicable)
        ascvd_risk = None
        if 40 <= features['age'] <= 79:
            try:
                ascvd_risk = ASCVDCalculator.calculate(
                    age=features['age'],
                    gender=features['gender'],
                    race='white',  # À améliorer avec vraies données
                    total_cholesterol=features['avg_cholesterol'],
                    hdl=features.get('avg_hdl', 50),
                    systolic_bp=features['avg_systolic_bp'],
                    on_bp_medication=False,
                    diabetic=False,
                    smoker=False
                )
            except Exception as e:
                logger.warning(f"ASCVD calculation failed: {e}")
        
        # Identifier les facteurs de risque
        risk_factors = cvd_model.identify_risk_factors(features)
        
        # Générer les recommandations
        recommendations = cvd_model.generate_recommendations(risk_category, risk_factors)
        
        # Sauvegarder la prédiction
        existing = session.query(RiskPrediction).filter_by(patient_id=patient_id).first()
        
        if existing:
            # Mettre à jour
            existing.framingham_score = framingham_score
            existing.ascvd_10year_risk = ascvd_risk
            existing.risk_category = risk_category
            existing.risk_factors = risk_factors
            existing.recommendations = recommendations
        else:
            # Créer nouveau
            prediction = RiskPrediction(
                patient_id=patient_id,
                framingham_score=framingham_score,
                ascvd_10year_risk=ascvd_risk,
                risk_category=risk_category,
                risk_factors=risk_factors,
                recommendations=recommendations
            )
            session.add(prediction)
        
        session.commit()
        session.close()
        
        return jsonify({
            'status': 'success',
            'patient_id': patient_id,
            'risk_assessment': {
                'overall_risk_percentage': risk_percentage,
                'risk_category': risk_category,
                'framingham_10year_risk': framingham_score,
                'ascvd_10year_risk': ascvd_risk
            },
            'risk_factors': risk_factors,
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        logger.error(f"Error predicting risk: {e}")
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/predict/all', methods=['POST'])
def predict_all():
    """Prédit le risque pour tous les patients avec des features"""
    try:
        session = Session()
        
        # Récupérer tous les patient IDs
        query = text("SELECT patient_id FROM patient_features")
        patients = session.execute(query).fetchall()
        session.close()
        
        results = []
        errors = []
        
        for patient in patients:
            patient_id = patient[0]
            try:
                result = predict_risk(patient_id)
                if result[1] == 200:
                    results.append(patient_id)
                else:
                    errors.append({'patient_id': patient_id, 'error': result[0].get_json()})
            except Exception as e:
                errors.append({'patient_id': patient_id, 'error': str(e)})
        
        return jsonify({
            'status': 'success',
            'predicted': len(results),
            'errors': len(errors),
            'patient_ids': results,
            'error_details': errors
        }), 200
        
    except Exception as e:
        logger.error(f"Error in bulk prediction: {e}")
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/risk/<patient_id>', methods=['GET'])
def get_risk_prediction(patient_id):
    """Récupère la prédiction de risque d'un patient"""
    try:
        session = Session()
        prediction = session.query(RiskPrediction).filter_by(patient_id=patient_id).first()
        session.close()
        
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404
        
        return jsonify(prediction.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error retrieving prediction: {e}")
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/stats', methods=['GET'])
def get_stats():
    """Statistiques sur les prédictions"""
    try:
        session = Session()
        
        from sqlalchemy import func
        
        total = session.query(func.count(RiskPrediction.id)).scalar()
        
        # Compter par catégorie de risque
        risk_counts = session.query(
            RiskPrediction.risk_category,
            func.count(RiskPrediction.id)
        ).group_by(RiskPrediction.risk_category).all()
        
        risk_distribution = {category: count for category, count in risk_counts}
        
        # Moyennes
        avg_framingham = session.query(func.avg(RiskPrediction.framingham_score)).scalar()
        avg_ascvd = session.query(func.avg(RiskPrediction.ascvd_10year_risk)).scalar()
        
        session.close()
        
        return jsonify({
            'total_predictions': total,
            'risk_distribution': risk_distribution,
            'average_framingham_score': round(avg_framingham, 2) if avg_framingham else None,
            'average_ascvd_risk': round(avg_ascvd, 2) if avg_ascvd else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/predictions', methods=['GET'])
def list_all_predictions():
    """Liste toutes les prédictions"""
    try:
        session = Session()
        all_predictions = session.query(RiskPrediction).all()
        session.close()
        
        return jsonify({
            'total': len(all_predictions),
            'predictions': [p.to_dict() for p in all_predictions]
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing predictions: {e}")
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/high-risk', methods=['GET'])
def get_high_risk_patients():
    """Liste les patients à haut risque"""
    try:
        session = Session()
        high_risk = session.query(RiskPrediction).filter_by(
            risk_category='high'
        ).all()
        session.close()

        return jsonify({
            'total': len(high_risk),
            'high_risk_patients': [p.to_dict() for p in high_risk]
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving high risk patients: {e}")
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/predictions/readmission', methods=['POST'])
def predict_readmission():
    """
    Predict 30-day readmission risk for a patient

    Request body:
    {
        "patient_id": "string",
        "features": {
            "age": 65,
            "num_medications": 12,
            "prior_admissions": 2,
            ... other features
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'features' not in data:
            return jsonify({'error': 'Missing features in request body'}), 400

        patient_id = data.get('patient_id', 'unknown')
        features = data['features']

        # Get prediction and SHAP explanations
        service = get_xgb_service()
        risk_score, shap_values = service.predict_readmission_risk(features)
        top_factors = service.get_top_risk_factors(shap_values, top_n=5)

        response = {
            'patient_id': patient_id,
            'readmission_risk': risk_score,
            'risk_category': 'high' if risk_score > 0.7 else 'medium' if risk_score > 0.4 else 'low',
            'top_risk_factors': top_factors,
            'shap_explanations': shap_values
        }

        logger.info(f"Prediction for patient {patient_id}: risk={risk_score:.3f}")

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500
 
