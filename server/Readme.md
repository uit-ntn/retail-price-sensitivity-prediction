# Retail Price Sensitivity API

FastAPI application for predicting retail customer price sensitivity, integrated with MLOps pipeline (Tasks 3-7).

## Chạy server đơn giản

### 1. Cài dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup biến môi trường (tùy chọn)
```bash
# Copy file mẫu
copy env.example .env

# Chỉnh sửa file .env với thông tin của bạn
# (Nếu không tạo .env, server sẽ dùng mock model)
```

### 3. Chạy server
```bash
python main.py
```

Server sẽ chạy tại: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## MLOps Pipeline Integration

### Task 3: S3 Data Storage Structure
```
s3://mlops-retail-prediction-dev-<account-id>/
├── raw/        # CSV gốc (~4.59GB)
├── silver/     # Parquet processed, partitioned  
├── gold/       # Feature engineered datasets
└── artifacts/  # SageMaker models (.tar.gz)
```

### Task 4: SageMaker Model Training
- Model artifacts: `artifacts/retail-price-sensitivity-model.tar.gz`
- Model Registry: SageMaker Model Package Groups
- Auto-extract from SageMaker tar.gz format

### Task 6-7: EKS Deployment  
- ECR repository: `mlops/retail-api`
- IRSA authentication (no hardcoded credentials)
- Namespace: `mlops-retail-forecast`

## Configuration (.env)

Tạo file `.env` từ `env.example`:

### Model Configuration (Tasks 3-4)
```bash
# S3 bucket từ Task 3 
MODEL_BUCKET=mlops-retail-prediction-dev-<account-id>
# SageMaker model từ Task 4
MODEL_KEY=artifacts/retail-price-sensitivity-model.tar.gz
# Gold dataset features
GOLD_DATA_PREFIX=gold/
MODEL_VERSION=1.0.0
```

### AWS Configuration (Task 2)
```bash
# Production: IRSA (no credentials needed)
# Development: local credentials
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key  
AWS_DEFAULT_REGION=us-east-1
```

### Data Pipeline (Task 3)
```bash
RAW_DATA_PREFIX=raw/
SILVER_DATA_PREFIX=silver/
ARTIFACTS_PREFIX=artifacts/
```

### SageMaker Integration (Task 4)  
```bash
SAGEMAKER_MODEL_NAME=retail-price-sensitivity-model
MODEL_REGISTRY_NAME=mlops-retail-model-package-group
```

## Model Loading Strategy

1. **SageMaker Artifacts** (.tar.gz) - Production
2. **Direct Model Files** (.joblib) - Development  
3. **Mock Model** - Fallback when S3 unavailable

**Lưu ý:** Nếu không có `.env`, server dùng mock model để test!
