"""
FastAPI application for Retail Price Sensitivity Prediction
Simple backend for serving ML model predictions
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
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
    description="ML-powered API for predicting customer price sensitivity",
    version="1.0.0"
)

# CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
model_loader = ModelLoader()
prediction_service = PredictionService(model_loader)


# Request/Response models
class PredictionRequest(BaseModel):
    """Input features for prediction"""
    BASKET_SIZE: str = Field(..., description="Basket size: S, M, or L")
    BASKET_TYPE: str = Field(..., description="Basket type: Full Shop, Top Up, etc.")
    STORE_REGION: str = Field(..., description="Store region code: E01-E05")
    STORE_FORMAT: str = Field(..., description="Store format: LS or SS")
    SPEND: float = Field(..., description="Total spend amount", ge=0)
    QUANTITY: int = Field(..., description="Number of items", ge=1)
    PROD_CODE_20: str = Field(..., description="Product category level 2")
    PROD_CODE_30: str = Field(..., description="Product category level 3")
    
    class Config:
        schema_extra = {
            "example": {
                "BASKET_SIZE": "M",
                "BASKET_TYPE": "Full Shop",
                "STORE_REGION": "E02",
                "STORE_FORMAT": "LS",
                "SPEND": 125.50,
                "QUANTITY": 15,
                "PROD_CODE_20": "DEP00053",
                "PROD_CODE_30": "G00016"
            }
        }


class PredictionResponse(BaseModel):
    """Prediction result"""
    prediction: str = Field(..., description="Predicted price sensitivity: Low, Medium, or High")
    probability: Dict[str, float] = Field(..., description="Probability for each class")
    confidence: float = Field(..., description="Confidence score (max probability)")
    model_version: str = Field(..., description="Model version used")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    model_version: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve simple HTML frontend"""
    html_file = Path(__file__).parent / "index.html"
    if html_file.exists():
        return html_file.read_text()
    return """
    <html>
        <head><title>Retail Prediction API</title></head>
        <body>
            <h1>Retail Price Sensitivity Prediction API</h1>
            <p>API is running. Visit <a href="/docs">/docs</a> for API documentation.</p>
        </body>
    </html>
    """


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for ALB and K8s"""
    model_info = model_loader.get_model_info()
    return HealthResponse(
        status="healthy" if model_info["loaded"] else "model_not_loaded",
        model_loaded=model_info["loaded"],
        model_version=model_info.get("version")
    )


@app.get("/ready")
async def readiness_check():
    """Readiness probe for K8s"""
    model_info = model_loader.get_model_info()
    if not model_info["loaded"]:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready"}


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make price sensitivity prediction
    
    Returns prediction class (Low/Medium/High) with probabilities
    """
    try:
        logger.info(f"Prediction request received: {request.dict()}")
        
        # Make prediction
        result = prediction_service.predict(request.dict())
        
        logger.info(f"Prediction result: {result['prediction']}")
        return PredictionResponse(**result)
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch")
async def predict_batch(requests: list[PredictionRequest]):
    """Batch prediction endpoint"""
    try:
        results = []
        for req in requests:
            result = prediction_service.predict(req.dict())
            results.append(result)
        return {"predictions": results}
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.get("/model/info")
async def model_info():
    """Get current model information"""
    return model_loader.get_model_info()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
