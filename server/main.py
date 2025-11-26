"""
FastAPI Application for Retail Price Sensitivity Prediction
Serves ML model predictions via REST API for MLOps pipeline
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import logging
from pathlib import Path

from model_loader import ModelLoader
from prediction_service import PredictionService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Retail Price Sensitivity Prediction API",
    description="ML model serving for retail customer price sensitivity prediction",
    version="1.0.0"
)

# CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model loader and prediction service
model_loader = ModelLoader()
prediction_service = PredictionService(model_loader)

# Pydantic models for request/response validation
class PredictionRequest(BaseModel):
    BASKET_SIZE: str = Field(..., description="Basket size: S, M, L")
    BASKET_TYPE: str = Field(..., description="Basket composition type")
    STORE_REGION: str = Field(..., description="Store region code")
    STORE_FORMAT: str = Field(..., description="Store format: SS (Small Store), LS (Large Store)")
    SPEND: float = Field(..., gt=0, description="Transaction spend amount in GBP")
    QUANTITY: int = Field(..., gt=0, description="Number of items purchased")
    PROD_CODE_20: str = Field(..., description="Product category level 2")
    PROD_CODE_30: str = Field(..., description="Product category level 3")

class PredictionResponse(BaseModel):
    prediction: str = Field(..., description="Predicted price sensitivity class")
    probability: Dict[str, float] = Field(..., description="Class probabilities")
    confidence: float = Field(..., description="Prediction confidence score")
    model_version: str = Field(..., description="Model version identifier")

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve HTML frontend for API testing"""
    html_path = Path(__file__).parent / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    return HTMLResponse("<h1>Retail Price Sensitivity Prediction API</h1><p>Visit /docs for API documentation</p>")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for ALB and Kubernetes probes"""
    try:
        model = model_loader.get_model()
        model_info = model_loader.get_model_info()
        
        return HealthResponse(
            status="healthy",
            model_loaded=model is not None,
            model_version=model_info.get("version", "unknown")
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness check endpoint for Kubernetes"""
    return await health_check()

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Single prediction endpoint"""
    try:
        # Convert request to dictionary
        features = request.dict()
        
        # Make prediction
        result = prediction_service.predict(features)
        
        return PredictionResponse(**result)
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict/batch")
async def predict_batch(requests: List[PredictionRequest]):
    """Batch prediction endpoint"""
    try:
        results = []
        for req in requests:
            features = req.dict()
            result = prediction_service.predict(features)
            results.append(result)
        
        return {"predictions": results, "count": len(results)}
    
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

@app.get("/model/info")
async def model_info():
    """Get model information"""
    try:
        info = model_loader.get_model_info()
        return info
    except Exception as e:
        logger.error(f"Model info error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
