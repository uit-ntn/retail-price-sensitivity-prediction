"""
Prediction service - Handles feature preprocessing and prediction logic
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for making predictions with preprocessing"""
    
    # Mapping for categorical features
    BASKET_SIZE_MAP = {'S': 0, 'M': 1, 'L': 2}
    STORE_FORMAT_MAP = {'SS': 0, 'LS': 1}
    
    # Class labels
    CLASS_LABELS = ['Low', 'Medium', 'High']
    
    def __init__(self, model_loader):
        self.model_loader = model_loader
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction from input features
        
        Args:
            features: Dictionary with feature values
            
        Returns:
            Dictionary with prediction, probabilities, and confidence
        """
        # Get model
        model = self.model_loader.get_model()
        if model is None:
            raise ValueError("Model not loaded")
        
        # Preprocess features
        processed_features = self._preprocess(features)
        
        # Make prediction
        prediction_idx = model.predict([processed_features])[0]
        
        # Get prediction class name
        if isinstance(prediction_idx, (int, np.integer)):
            prediction_class = self.CLASS_LABELS[prediction_idx]
        else:
            prediction_class = str(prediction_idx)
        
        # Get probabilities if available
        probabilities = {}
        confidence = 1.0
        
        try:
            proba = model.predict_proba([processed_features])[0]
            probabilities = {
                label: float(prob) 
                for label, prob in zip(self.CLASS_LABELS, proba)
            }
            confidence = float(max(proba))
        except AttributeError:
            # Model doesn't support predict_proba
            probabilities = {prediction_class: 1.0}
        
        # Get model version
        model_info = self.model_loader.get_model_info()
        
        return {
            "prediction": prediction_class,
            "probability": probabilities,
            "confidence": confidence,
            "model_version": model_info.get("version", "unknown")
        }
    
    def _preprocess(self, features: Dict[str, Any]) -> list:
        """
        Preprocess input features for model
        
        Simple preprocessing for demonstration - converts categorical to numeric
        In production, use same preprocessing pipeline as training
        """
        # Extract and encode features
        processed = []
        
        # Encode BASKET_SIZE
        basket_size = self.BASKET_SIZE_MAP.get(features.get('BASKET_SIZE', 'M'), 1)
        processed.append(basket_size)
        
        # Encode STORE_FORMAT
        store_format = self.STORE_FORMAT_MAP.get(features.get('STORE_FORMAT', 'LS'), 1)
        processed.append(store_format)
        
        # Hash categorical features (simplified encoding)
        basket_type = hash(features.get('BASKET_TYPE', '')) % 100
        processed.append(basket_type)
        
        store_region = hash(features.get('STORE_REGION', '')) % 10
        processed.append(store_region)
        
        # Numeric features
        processed.append(float(features.get('SPEND', 0)))
        processed.append(int(features.get('QUANTITY', 0)))
        
        # Product codes (hash encoding)
        prod_code_20 = hash(features.get('PROD_CODE_20', '')) % 100
        processed.append(prod_code_20)
        
        prod_code_30 = hash(features.get('PROD_CODE_30', '')) % 100
        processed.append(prod_code_30)
        
        logger.debug(f"Preprocessed features: {processed}")
        return processed
