"""
Model Loader for Retail Price Sensitivity Prediction
Handles model download from S3 and local caching
"""

import os
import joblib
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

class ModelLoader:
    """Load ML model from S3 or use mock model for testing"""
    
    def __init__(self):
        self.model = None
        self.model_path = "/tmp/model.joblib"
        self.bucket_name = os.getenv("MODEL_BUCKET", "mlops-retail-forecast-models")
        self.model_key = os.getenv("MODEL_KEY", "models/retail-price-sensitivity/model.joblib")
        
        # Load model on initialization
        self.load_model()
    
    def load_model(self):
        """Load model from S3 or use mock model"""
        try:
            # Try to load from S3
            logger.info(f"Attempting to load model from S3: s3://{self.bucket_name}/{self.model_key}")
            self._download_from_s3()
            self.model = self._load_from_file()
            logger.info("Model loaded successfully from S3")
            
        except Exception as e:
            logger.warning(f"Failed to load model from S3: {str(e)}")
            logger.info("Using mock model for testing")
            self.model = self._load_mock_model()
    
    def _download_from_s3(self):
        """Download model file from S3"""
        try:
            import boto3
            
            s3_client = boto3.client('s3')
            
            # Download model file
            s3_client.download_file(
                Bucket=self.bucket_name,
                Key=self.model_key,
                Filename=self.model_path
            )
            
            logger.info(f"Model downloaded to {self.model_path}")
            
        except Exception as e:
            logger.error(f"S3 download failed: {str(e)}")
            raise
    
    def _load_from_file(self):
        """Load model from local file"""
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        model = joblib.load(self.model_path)
        logger.info("Model loaded from file")
        return model
    
    def _load_mock_model(self):
        """Create mock model for testing when S3 is unavailable"""
        
        class MockModel:
            """Simple mock model for testing"""
            
            def predict(self, X):
                """Predict price sensitivity based on simple rules"""
                predictions = []
                
                for row in X:
                    # Simple rule-based prediction
                    # Assuming SPEND is in position 4 (index 4)
                    spend = row[4] if len(row) > 4 else 100
                    
                    if spend < 50:
                        predictions.append(2)  # High sensitivity
                    elif spend < 150:
                        predictions.append(1)  # Medium sensitivity
                    else:
                        predictions.append(0)  # Low sensitivity
                
                return np.array(predictions)
            
            def predict_proba(self, X):
                """Return mock probabilities"""
                predictions = self.predict(X)
                probas = []
                
                for pred in predictions:
                    if pred == 0:  # Low
                        probas.append([0.7, 0.2, 0.1])
                    elif pred == 1:  # Medium
                        probas.append([0.2, 0.6, 0.2])
                    else:  # High
                        probas.append([0.1, 0.2, 0.7])
                
                return np.array(probas)
        
        logger.info("Mock model created")
        return MockModel()
    
    def get_model(self):
        """Get loaded model instance"""
        if self.model is None:
            raise ValueError("Model not loaded")
        return self.model
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model metadata"""
        info = {
            "model_loaded": self.model is not None,
            "model_type": type(self.model).__name__,
            "model_source": "s3" if Path(self.model_path).exists() else "mock",
            "version": os.getenv("MODEL_VERSION", "1.0.0")
        }
        
        if Path(self.model_path).exists():
            info["model_path"] = self.model_path
            info["model_size_mb"] = round(Path(self.model_path).stat().st_size / (1024 * 1024), 2)
        
        return info
    
    def reload_model(self):
        """Reload model from S3"""
        logger.info("Reloading model...")
        self.model = None
        
        # Remove cached model file
        if Path(self.model_path).exists():
            Path(self.model_path).unlink()
        
        # Reload model
        self.load_model()
        logger.info("Model reloaded successfully")
