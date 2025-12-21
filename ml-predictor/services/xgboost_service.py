import xgboost as xgb
import shap
import numpy as np
import os
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class XGBoostPredictionService:
    """Service for XGBoost model loading and SHAP-based predictions"""

    def __init__(self, model_path: str = None):
        requested_path = model_path or os.getenv('XGBOOST_MODEL_PATH', '../xgboost_readmission_model.ubj')
        self.model_path = self._resolve_model_path(requested_path)
        self.model = None
        self.explainer = None
        self.load_model()

    def _resolve_model_path(self, requested_path: str) -> str:
        """Return the first available model path (UBJ preferred, JSON fallback)."""
        candidates = [requested_path]

        if requested_path.endswith('.ubj'):
            candidates.append(requested_path[:-4] + '.json')
        elif requested_path.endswith('.json'):
            candidates.insert(0, requested_path[:-5] + '.ubj')

        for candidate in candidates:
            if os.path.exists(candidate):
                if candidate != requested_path:
                    logger.warning(
                        f"Requested model '{requested_path}' absent. Using fallback '{candidate}'."
                    )
                return candidate

        raise FileNotFoundError(
            f"No XGBoost model found. Checked: {', '.join(candidates)}"
        )

    def load_model(self):
        """Load XGBoost model from UBJ (preferred) or JSON."""
        try:
            self.model = xgb.Booster()
            self.model.load_model(self.model_path)

            # Initialize SHAP explainer
            self.explainer = shap.TreeExplainer(self.model)

            logger.info(f"XGBoost model loaded successfully from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load XGBoost model: {str(e)}")
            raise

    def predict_readmission_risk(self, features: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        """
        Predict 30-day readmission risk with SHAP explanations

        Args:
            features: Dictionary of patient features

        Returns:
            Tuple of (risk_score, shap_values_dict)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")

        try:
            # Convert features dict to numpy array (assumes feature order matches training)
            feature_names = sorted(features.keys())
            feature_array = np.array([[features[name] for name in feature_names]])

            # Convert to DMatrix for XGBoost
            dmatrix = xgb.DMatrix(feature_array, feature_names=feature_names)

            # Get prediction (probability of readmission)
            prediction = self.model.predict(dmatrix)[0]

            # Calculate SHAP values for explanation
            shap_values = self.explainer.shap_values(feature_array)

            # Create SHAP explanation dictionary
            shap_dict = {
                name: float(shap_values[0][i])
                for i, name in enumerate(feature_names)
            }

            # Sort by absolute SHAP value (most important features first)
            shap_dict = dict(sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True))

            return float(prediction), shap_dict

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise

    def get_top_risk_factors(self, shap_values: Dict[str, float], top_n: int = 5) -> List[Dict[str, any]]:
        """
        Extract top N risk factors from SHAP values

        Args:
            shap_values: Dictionary of SHAP values
            top_n: Number of top factors to return

        Returns:
            List of top risk factors with feature name, SHAP value, and direction
        """
        sorted_features = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)[:top_n]

        return [
            {
                'feature': feature_name,
                'shap_value': shap_value,
                'direction': 'increases_risk' if shap_value > 0 else 'decreases_risk',
                'magnitude': abs(shap_value)
            }
            for feature_name, shap_value in sorted_features
        ]
