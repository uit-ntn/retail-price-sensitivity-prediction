# Azure Machine Learning - Retail Forecast MLOps

Thư mục này chứa tất cả **Azure ML components** cho **training, deployment, và environment management** trong Retail Forecast MLOps pipeline.

---

## 📁 Cấu trúc thư mục

```
aml/
├── train-job.yml            # Azure ML training job definition
├── train.Dockerfile         # Training container image
├── infer.Dockerfile         # Inference container image
├── deployment/              # Online endpoint deployment configs
│   ├── endpoint.yml         # Managed online endpoint definition
│   └── blue.yml            # Blue deployment configuration
├── environments/            # ML environments
│   └── conda.yml           # Conda environment for training
└── README.MD               # File này
```

---

## 🚀 Training Components

### `train-job.yml` - Azure ML Training Job
**Command Job** definition cho model training:

```yaml
$schema: https://azuremlschemas.azureedge.net/latest/commandJob.schema.json
display_name: retail-train
experiment_name: retail-demand-forecast
code: ../src
command: >-
  python train.py --data ${{inputs.train_data}} --out_dir ${{outputs.model_out}}
environment:
  image: <to-be-overridden-by-pipeline>
compute: azureml:cpu-cluster
inputs:
  train_data:
    type: uri_folder
    path: azureml://datastores/workspaceblobstore/paths/data/train/
outputs:
  model_out:
    type: uri_folder
```

**Key Features:**
- **Experiment Tracking:** `retail-demand-forecast` experiment
- **Parameterized Inputs:** Training data path
- **Flexible Environment:** Image overridden by pipeline
- **Compute Target:** CPU cluster với auto-scaling
- **Output Management:** Model artifacts to workspace storage

**Usage:**
```bash
# Submit training job
az ml job create --file train-job.yml

# Override parameters
az ml job create --file train-job.yml \
  --set inputs.train_data.path=azureml://datastores/workspaceblobstore/paths/data/custom/
```

### `train.Dockerfile` - Training Container
**Container definition** cho training environment:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Training code sẽ được mount vào /app/src
COPY src/ /app/src/

CMD ["python", "src/train.py"]
```

**Features:**
- **Base Image:** Python 3.10 slim
- **Dependencies:** ML libraries (sklearn, mlflow, etc.)
- **Code Mount:** Source code mounted at runtime
- **Optimized:** No-cache pip install

**Build & Push:**
```bash
# Build training image
docker build -f train.Dockerfile -t acrretaildev.azurecr.io/retail/train:latest .

# Push to ACR
az acr login --name acrretaildev
docker push acrretaildev.azurecr.io/retail/train:latest
```

---

## 🔄 Deployment Components

### `deployment/endpoint.yml` - Online Endpoint
**Managed Online Endpoint** definition:

```yaml
$schema: https://azuremlschemas.azureedge.net/latest/managedOnlineEndpoint.schema.json
name: retail-forecast-endpoint
auth_mode: key  # hoặc 'aml_token' nếu dùng AAD
tags:
  project: retail-forecast
  env: dev
```

**Configuration:**
- **Authentication:** Key-based (simple) hoặc AAD token
- **Naming:** Environment-specific naming
- **Tagging:** Project và environment tags

**Deployment:**
```bash
# Create endpoint
az ml online-endpoint create --file deployment/endpoint.yml

# Check status
az ml online-endpoint show --name retail-forecast-endpoint
```

### `deployment/blue.yml` - Blue Deployment
**Blue-Green deployment** configuration:

```yaml
$schema: https://azuremlschemas.azureedge.net/latest/managedOnlineDeployment.schema.json
name: blue
endpoint_name: retail-forecast-endpoint

# Model đã đăng ký trong AML
model: azureml:retail-forecast@latest

# BYOC: Custom container từ ACR
environment:
  image: ACR_NAME.azurecr.io/retail/infer:IMAGE_TAG

instance_type: Standard_DS3_v2
instance_count: 1

app_insights_enabled: true

liveness_route:
  path: /health
  port: 8080
readiness_route:
  path: /health
  port: 8080

request_settings:
  request_timeout_ms: 60000
  max_concurrent_requests_per_instance: 1
  max_queue_wait_ms: 60000

scale_settings:
  type: default
  min_instances: 1
  max_instances: 3
```

**Key Features:**

#### **Model Integration:**
- **Model Reference:** `azureml:retail-forecast@latest`
- **Automatic Versioning:** Latest registered model
- **Model Lineage:** Full tracking từ training job

#### **Container Configuration:**
- **BYOC (Bring Your Own Container):** Custom inference image
- **ACR Integration:** Pull từ Azure Container Registry
- **Flexible Tagging:** Build ID hoặc semantic versioning

#### **Scaling & Performance:**
- **Instance Type:** Standard_DS3_v2 (4 vCPU, 14 GB RAM)
- **Auto-scaling:** 1-3 instances
- **Request Handling:** 1 concurrent request per instance
- **Timeout:** 60-second request timeout

#### **Health Monitoring:**
- **Health Checks:** `/health` endpoint
- **Application Insights:** Full telemetry enabled
- **Port Configuration:** 8080 (FastAPI default)

**Deployment:**
```bash
# Deploy blue version
az ml online-deployment create --file deployment/blue.yml

# Set traffic to 100% blue
az ml online-endpoint update --name retail-forecast-endpoint --traffic "blue=100"

# Test deployment
az ml online-endpoint invoke \
  --name retail-forecast-endpoint \
  --request-file test_data.json
```

### `infer.Dockerfile` - Inference Container
**FastAPI inference** container:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/

EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Features:**
- **FastAPI Framework:** High-performance async API
- **Health Endpoint:** `/health` cho Azure ML health checks
- **Model Loading:** Load model từ Azure ML workspace
- **Monitoring:** Application Insights integration

---

## 🌍 Environment Management

### `environments/conda.yml` - Training Environment
**Conda environment** cho training jobs:

```yaml
name: retail-train-env
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.10
  - pip
  - pip:
      - numpy
      - pandas
      - scikit-learn
      - mlflow
      - azureml-mlflow
      - pyarrow
      - joblib
      - matplotlib
```

**Dependencies:**
- **Core ML:** scikit-learn, numpy, pandas
- **Experiment Tracking:** MLflow với Azure ML integration
- **Data Handling:** pyarrow cho efficient data loading
- **Visualization:** matplotlib cho plots
- **Model Serialization:** joblib cho model persistence

**Usage:**
```bash
# Create AML environment từ conda.yml
az ml environment create --file environments/conda.yml

# Use in training job
az ml job create --file train-job.yml \
  --set environment=azureml:retail-train-env@latest
```

---

## 🚀 Complete ML Workflow

### 1. **Training Pipeline**
```bash
#!/bin/bash
set -e

echo "🚀 Starting ML Training Pipeline"

# Step 1: Build và push training image
echo "📦 Building training container..."
docker build -f train.Dockerfile -t acrretaildev.azurecr.io/retail/train:$(git rev-parse --short HEAD) .
docker push acrretaildev.azurecr.io/retail/train:$(git rev-parse --short HEAD)

# Step 2: Submit training job
echo "🏋️ Submitting training job..."
az ml job create --file train-job.yml \
  --set environment.image=acrretaildev.azurecr.io/retail/train:$(git rev-parse --short HEAD)

# Step 3: Wait for completion
JOB_NAME=$(az ml job list --query "[0].name" -o tsv)
az ml job stream --name $JOB_NAME

echo "✅ Training completed!"
```

### 2. **Model Registration**
```bash
#!/bin/bash
set -e

echo "📝 Registering trained model..."

# Get latest training job
JOB_NAME=$(az ml job list --query "[0].name" -o tsv)

# Register model from job output
az ml model create \
  --name retail-forecast \
  --version auto \
  --path "azureml://jobs/$JOB_NAME/outputs/model_out" \
  --type mlflow_model

echo "✅ Model registered successfully!"
```

### 3. **Deployment Pipeline**
```bash
#!/bin/bash
set -e

echo "🚀 Starting Deployment Pipeline"

# Step 1: Build và push inference image
echo "📦 Building inference container..."
docker build -f infer.Dockerfile -t acrretaildev.azurecr.io/retail/infer:$(git rev-parse --short HEAD) .
docker push acrretaildev.azurecr.io/retail/infer:$(git rev-parse --short HEAD)

# Step 2: Update deployment configuration
sed -i "s/IMAGE_TAG/$(git rev-parse --short HEAD)/g" deployment/blue.yml
sed -i "s/ACR_NAME/acrretaildev/g" deployment/blue.yml

# Step 3: Create endpoint (if not exists)
az ml online-endpoint create --file deployment/endpoint.yml --no-wait || true

# Step 4: Deploy blue version
echo "🔵 Deploying blue version..."
az ml online-deployment create --file deployment/blue.yml --all-traffic

# Step 5: Test deployment
echo "🧪 Testing deployment..."
az ml online-endpoint invoke \
  --name retail-forecast-endpoint \
  --request-file test_data.json

echo "✅ Deployment completed successfully!"
```

---

## 📊 Monitoring & Logging

### Application Insights Integration:
```yaml
# In blue.yml
app_insights_enabled: true
```

**Metrics Collected:**
- Request latency và throughput
- Error rates và exceptions
- Resource utilization (CPU, memory)
- Custom business metrics

### Health Monitoring:
```yaml
liveness_route:
  path: /health
  port: 8080
readiness_route:
  path: /health
  port: 8080
```

**Health Check Implementation:**
```python
# In FastAPI app
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Log Queries:
```bash
# View deployment logs
az ml online-deployment get-logs \
  --name blue \
  --endpoint retail-forecast-endpoint

# Monitor real-time logs
az ml online-deployment get-logs \
  --name blue \
  --endpoint retail-forecast-endpoint \
  --follow
```

---

## 🔧 Configuration Management

### Environment Variables:
```bash
# Required for deployment
export ACR_NAME="acrretaildev"
export RESOURCE_GROUP="retail-dev-rg"
export WORKSPACE_NAME="retail-dev-amlws"
export ENDPOINT_NAME="retail-forecast-endpoint"

# Optional configurations
export MODEL_NAME="retail-forecast"
export MODEL_VERSION="latest"
export INSTANCE_TYPE="Standard_DS3_v2"
```

### Parameter Overrides:
```bash
# Override training parameters
az ml job create --file train-job.yml \
  --set compute=azureml:gpu-cluster \
  --set inputs.train_data.path=azureml://datastores/mydatastore/paths/custom/

# Override deployment settings
az ml online-deployment create --file deployment/blue.yml \
  --set instance_count=2 \
  --set scale_settings.max_instances=5
```

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. **Training Job Failures**
```bash
# Check job logs
az ml job stream --name <job-name>

# Download job logs
az ml job download --name <job-name> --output-name logs

# Check compute status
az ml compute show --name cpu-cluster
```

#### 2. **Deployment Issues**
```bash
# Check endpoint status
az ml online-endpoint show --name retail-forecast-endpoint

# Check deployment logs
az ml online-deployment get-logs --name blue --endpoint retail-forecast-endpoint

# Test endpoint connectivity
az ml online-endpoint invoke --name retail-forecast-endpoint --request-file test.json
```

#### 3. **Container Issues**
```bash
# Test container locally
docker run -p 8080:8080 acrretaildev.azurecr.io/retail/infer:latest

# Check ACR permissions
az acr check-health --name acrretaildev

# Test health endpoint
curl http://localhost:8080/health
```

#### 4. **Model Loading Issues**
```bash
# Check model registration
az ml model show --name retail-forecast --version latest

# Verify model artifacts
az ml model download --name retail-forecast --version latest --download-path ./model
```

---

## 💰 Cost Optimization

### 1. **Compute Optimization**
```yaml
# Use smaller instances for inference
instance_type: Standard_DS2_v2  # 2 vCPU, 7 GB RAM

# Scale to zero khi không sử dụng
scale_settings:
  type: default
  min_instances: 0  # Scale to zero
  max_instances: 3
```

### 2. **Training Optimization**
```bash
# Use spot instances for training
az ml job create --file train-job.yml \
  --set compute=azureml:spot-cluster
```

### 3. **Storage Optimization**
```bash
# Clean up old model versions
az ml model archive --name retail-forecast --version 1

# Delete unused environments
az ml environment archive --name retail-train-env --version 1
```

---

## 🔄 Blue-Green Deployment Strategy

### Green Deployment:
```yaml
# deployment/green.yml
name: green
endpoint_name: retail-forecast-endpoint
model: azureml:retail-forecast@latest
environment:
  image: acrretaildev.azurecr.io/retail/infer:v2.0.0
# ... same config as blue
```

### Traffic Splitting:
```bash
# Deploy green version (0% traffic)
az ml online-deployment create --file deployment/green.yml

# Test green deployment
az ml online-endpoint invoke \
  --name retail-forecast-endpoint \
  --deployment green \
  --request-file test.json

# Gradually shift traffic
az ml online-endpoint update --name retail-forecast-endpoint --traffic "blue=50,green=50"
az ml online-endpoint update --name retail-forecast-endpoint --traffic "blue=0,green=100"

# Delete old blue deployment
az ml online-deployment delete --name blue --endpoint retail-forecast-endpoint
```

---

## 📚 Tài liệu tham khảo

- [Azure ML CLI v2](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli)
- [Azure ML Online Endpoints](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-online-endpoints)
- [Azure ML Training Jobs](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-train-model)
- [Azure ML Environments](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-manage-environments-v2)
- [MLflow on Azure ML](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-mlflow)
