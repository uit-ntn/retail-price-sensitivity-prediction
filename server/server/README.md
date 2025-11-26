# Server - FastAPI Retail Prediction API

Backend API service cho Retail Price Sensitivity Prediction.

## 📁 Cấu trúc thư mục

```
server/
├── main.py                 # FastAPI application entry point
├── model_loader.py         # Load ML model từ S3
├── prediction_service.py   # Prediction logic & preprocessing
├── health_check.py         # Health check for Docker/K8s
├── index.html              # Web UI (TailwindCSS)
├── requirements.txt        # Python dependencies
└── Dockerfile             # Container build file
```

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Truy cập:
- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Docker Build

```bash
# Build image
docker build -t retail-api:latest .

# Run container
docker run -d -p 8000:8000 \
  -e MODEL_BUCKET=mlops-retail-forecast-models \
  -e MODEL_KEY=models/retail-price-sensitivity/model.joblib \
  --name retail-api \
  retail-api:latest
```

## 📡 API Endpoints

### GET /
Web UI với TailwindCSS để test API

### GET /health
Health check endpoint
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "v1.0"
}
```

### POST /predict
Dự đoán price sensitivity

**Request:**
```json
{
  "BASKET_SIZE": "M",
  "BASKET_TYPE": "Full Shop",
  "STORE_REGION": "E02",
  "STORE_FORMAT": "LS",
  "SPEND": 125.50,
  "QUANTITY": 15,
  "PROD_CODE_20": "DEP00053",
  "PROD_CODE_30": "G00016"
}
```

**Response:**
```json
{
  "prediction": "Medium",
  "probability": {
    "Low": 0.2,
    "Medium": 0.6,
    "High": 0.2
  },
  "confidence": 0.6,
  "model_version": "v1.0"
}
```

### GET /model/info
Thông tin model hiện tại

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_BUCKET` | `mlops-retail-forecast-models` | S3 bucket chứa model |
| `MODEL_KEY` | `models/retail-price-sensitivity/model.joblib` | S3 key của model file |
| `AWS_DEFAULT_REGION` | `ap-southeast-1` | AWS region |

## 🧪 Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "BASKET_SIZE": "M",
    "BASKET_TYPE": "Full Shop",
    "STORE_REGION": "E02",
    "STORE_FORMAT": "LS",
    "SPEND": 125.50,
    "QUANTITY": 15,
    "PROD_CODE_20": "DEP00053",
    "PROD_CODE_30": "G00016"
  }'
```

## 📝 Features

✅ FastAPI với automatic OpenAPI docs  
✅ Model loading từ S3 với fallback mock model  
✅ Health check cho ALB và Kubernetes  
✅ CORS enabled cho web frontend  
✅ Non-root user trong Docker  
✅ Multi-stage build để giảm image size  
✅ Web UI đẹp với TailwindCSS  

## 🔐 Security

- Container chạy với non-root user (`apiuser`)
- No AWS credentials hardcoded (dùng IAM roles)
- CORS configured (update cho production)
- Health check endpoint cho monitoring

## 📊 Model Loading

Service tự động tải model từ S3 khi khởi động. Nếu không tải được model từ S3 (ví dụ trong local dev), service sẽ fallback sang mock model để test.

Mock model dùng rule-based logic:
- Spend < £50 → High sensitivity
- Spend £50-£150 → Medium sensitivity  
- Spend > £150 → Low sensitivity
