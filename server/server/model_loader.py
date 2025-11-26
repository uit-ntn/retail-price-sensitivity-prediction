"""
Model loader - Downloads and caches ML model from S3
"""
import os
import pickle
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class ModelLoader:
    """Load and cache ML model from S3"""
    
    def __init__(self):
        self.model = None
        self.model_version = None
        self.s3_client = boto3.client('s3')
        
        # Configuration from environment variables
        self.bucket = os.getenv('MODEL_BUCKET', 'mlops-retail-forecast-models')
        self.model_key = os.getenv('MODEL_KEY', 'models/retail-price-sensitivity/model.joblib')
        self.local_model_path = Path('/tmp/model.joblib')
        
        # Auto-load model on initialization
        self.load_model()
    
    def load_model(self) -> bool:
        """
        Download model from S3 and load into memory
        Returns True if successful
        """
        try:
            # Check if model already exists locally
            if self.local_model_path.exists():
                logger.info(f"Loading cached model from {self.local_model_path}")
                self.model = self._load_from_file(self.local_model_path)
                return True
            
            # Download from S3
            logger.info(f"Downloading model from s3://{self.bucket}/{self.model_key}")
            self.s3_client.download_file(
                self.bucket,
                self.model_key,
                str(self.local_model_path)
            )
            
            # Load model
            self.model = self._load_from_file(self.local_model_path)
            
            # Get model metadata
            try:
                metadata = self.s3_client.head_object(
                    Bucket=self.bucket,
                    Key=self.model_key
                )
                self.model_version = metadata.get('VersionId', 'unknown')
            except ClientError:
                self.model_version = 'unknown'
            
            logger.info(f"Model loaded successfully. Version: {self.model_version}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to download model from S3: {e}")
            # Fallback to mock model for testing
            self._load_mock_model()
            return False
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._load_mock_model()
            return False
    
    def _load_from_file(self, path: Path):
        """Load model from file (supports pickle/joblib)"""
        try:
            import joblib
            return joblib.load(path)
        except Exception:
            with open(path, 'rb') as f:
                return pickle.load(f)
    
    def _load_mock_model(self):
        """Load a simple mock model for testing when S3 model unavailable"""
        logger.warning("Using mock model for testing")
        
        class MockModel:
            def predict(self, X):
                # Simple rule-based prediction for testing
                import numpy as np
                predictions = []
                for features in X:
                    spend = features[4] if len(features) > 4 else 50
                    if spend < 50:
                        predictions.append('High')
                    elif spend < 150:
                        predictions.append('Medium')
                    else:
                        predictions.append('Low')
                return np.array(predictions)
            
            def predict_proba(self, X):
                import numpy as np
                predictions = self.predict(X)
                proba = []
                for pred in predictions:
                    if pred == 'High':
                        proba.append([0.1, 0.2, 0.7])  # [Low, Medium, High]
                    elif pred == 'Medium':
                        proba.append([0.2, 0.6, 0.2])
                    else:
                        proba.append([0.7, 0.2, 0.1])
                return np.array(proba)
        
        self.model = MockModel()
        self.model_version = "mock-v1"
    
    def get_model(self):
        """Get the loaded model instance"""
        if self.model is None:
            self.load_model()
        return self.model
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model metadata"""
        return {
            "loaded": self.model is not None,
            "version": self.model_version,
            "bucket": self.bucket,
            "key": self.model_key,
            "local_path": str(self.local_model_path)
        }
    
    def reload_model(self) -> bool:
        """Force reload model from S3"""
        if self.local_model_path.exists():
            self.local_model_path.unlink()
        self.model = None
        return self.load_model()
