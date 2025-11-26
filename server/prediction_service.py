"""
Prediction Service for Retail Price Sensitivity
Handles feature preprocessing and model inference
"""

import logging
import numpy as np
from typing import Dict, Any
from model_loader import ModelLoader

logger = logging.getLogger(__name__)

class PredictionService:
    """Service for preprocessing features and making predictions"""
    
    # Class labels mapping
    CLASS_LABELS = ['Low', 'Medium', 'High']
    
    # Feature encoding maps
    BASKET_SIZE_MAP = {'S': 0, 'M': 1, 'L': 2}
    STORE_FORMAT_MAP = {'SS': 0, 'LS': 1}
    
    def __init__(self, model_loader: ModelLoader):
        self.model_loader = model_loader
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction for given features
        
        Args:
            features: Dictionary with customer transaction features
            
        Returns:
            Dictionary with prediction, probabilities, and confidence
        """
        try:
            # Preprocess features
            X = self._preprocess(features)
            
            # Get model
            model = self.model_loader.get_model()
            
            # Make prediction
            prediction = model.predict(X)[0]
            probabilities = model.predict_proba(X)[0]
            
            # Get class label
            class_label = self.CLASS_LABELS[prediction]
            
            # Get confidence (max probability)
            confidence = float(max(probabilities))
            
            # Build probability dictionary
            prob_dict = {
                label: float(prob) 
                for label, prob in zip(self.CLASS_LABELS, probabilities)
            }
            
            # Get model info
            model_info = self.model_loader.get_model_info()
            
            return {
                "prediction": class_label,
                "probability": prob_dict,
                "confidence": round(confidence, 4),
                "model_version": model_info.get("version", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
    
    def _preprocess(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Preprocess features for model input
        
        Args:
            features: Raw feature dictionary
            
        Returns:
            Preprocessed feature array
        """
        try:
            # Extract and encode features
            basket_size_encoded = self.BASKET_SIZE_MAP.get(features['BASKET_SIZE'], 1)
            store_format_encoded = self.STORE_FORMAT_MAP.get(features['STORE_FORMAT'], 0)
            
            # Hash categorical features (simple hash for demo)
            basket_type_hash = hash(features['BASKET_TYPE']) % 100
            store_region_hash = hash(features['STORE_REGION']) % 100
            prod_code_20_hash = hash(features['PROD_CODE_20']) % 1000
            prod_code_30_hash = hash(features['PROD_CODE_30']) % 1000
            
            # Build feature array
            # Order: BASKET_SIZE, BASKET_TYPE, STORE_REGION, STORE_FORMAT, 
            #        SPEND, QUANTITY, PROD_CODE_20, PROD_CODE_30
            feature_array = np.array([[
                basket_size_encoded,
                basket_type_hash,
                store_region_hash,
                store_format_encoded,
                features['SPEND'],
                features['QUANTITY'],
                prod_code_20_hash,
                prod_code_30_hash
            ]])
            
            logger.debug(f"Preprocessed features: {feature_array}")
            return feature_array
            
        except KeyError as e:
            logger.error(f"Missing required feature: {str(e)}")
            raise ValueError(f"Missing required feature: {str(e)}")
        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}")
            raise
