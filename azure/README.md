# Azure MLOps Setup - Retail Forecast

Thư mục này chứa tất cả cấu hình để triển khai **Retail Forecast MLOps pipeline** trên **Microsoft Azure**.

---

## 📁 Cấu trúc thư mục

```
azure/
├── aml/                    # Azure Machine Learning
│   ├── train.Dockerfile    # Container image cho training job
│   ├── infer.Dockerfile    # Container image cho inference API
│   └── train-job.yml       # Job definition cho AML training
│
├── infra/                  # Infrastructure as Code (Bicep)
│   └── main.bicep          # Tạo AKS, ACR, AML workspace, Storage
│
├── k8s/                    # Kubernetes manifests cho AKS
│   ├── deployment.yaml     # Deploy inference API pods
│   ├── service.yaml        # Expose API service
│   └── hpa.yaml           # Horizontal Pod Autoscaler
│
├── monitor/                # Monitoring & Observability
│   ├── alerts.bicep        # Application Insights alerts setup
│   └── kql/               # KQL queries cho monitoring
│       ├── error.kql      # Query lỗi và 5xx responses
│       └── latency.kql    # Query p50/p95/p99 latency
│
├── azure-pipelines.yml     # Azure DevOps CI/CD pipeline
└── README.md              # File này
```

---

## 🏗️ Infrastructure Setup (`infra/`)

### `main.bicep`
File Bicep này tạo toàn bộ hạ tầng Azure cần thiết:

**Resources được tạo:**
- **Storage Account** (`stmlretail`) - Lưu trữ data, models, logs
- **Container Registry** (`acrmlretail`) - Lưu Docker images
- **Azure ML Workspace** (`mlw-retail`) - Quản lý ML lifecycle
- **AKS Cluster** (`aks-mlops-prod`) - Kubernetes cluster cho inference

**Deploy infrastructure:**
```bash
# Tạo resource group trước
az group create --name rg-mlops --location southeastasia

# Deploy Bicep template
az deployment group create \
  --resource-group rg-mlops \
  --template-file infra/main.bicep \
  --parameters \
    location=southeastasia \
    workspaceName=mlw-retail \
    storageName=stmlretail \
    acrName=acrmlretail \
    aksName=aks-mlops-prod
```

---

## 🤖 Azure Machine Learning (`aml/`)

### `train.Dockerfile`
Container definition cho **training jobs** trên Azure ML.

**Chức năng:**
- Base image: Python 3.10 slim
- Cài đặt ML dependencies (sklearn, pandas, mlflow)
- Copy training code và chạy training script
- Output: Trained model artifacts

**Sử dụng:**
```bash
# Build local (test)
docker build -f aml/train.Dockerfile -t train-image .

# Hoặc để Azure DevOps build tự động
```

### `infer.Dockerfile`
Container definition cho **inference API**.

**Chức năng:**
- Base image: Python 3.10 slim
- Cài đặt FastAPI, uvicorn cho API serving
- Copy inference code và model
- Expose port 80 cho HTTP requests

**Sử dụng:**
```bash
# Build local
docker build -f aml/infer.Dockerfile -t infer-image .

# Run local test
docker run -p 8080:80 infer-image
```

### `train-job.yml`
Azure ML job definition cho **training workflow**.

**Cấu hình:**
- Compute target: AML compute cluster
- Environment: Custom Docker image từ `train.Dockerfile`
- Input data: Từ Azure Storage hoặc datastore
- Output: Model artifacts được register vào AML Model Registry

**Submit job:**
```bash
# Sử dụng Azure ML CLI v2
az ml job create --file aml/train-job.yml --resource-group rg-mlops --workspace-name mlw-retail
```

---

## ☸️ Kubernetes Deployment (`k8s/`)

### `deployment.yaml`
Kubernetes Deployment cho **inference API pods**.

**Cấu hình:**
- **Replicas:** 3 pods (high availability)
- **Image:** `<ACR_NAME>.azurecr.io/infer:latest`
- **Port:** 80 (HTTP)
- **Environment:** Model path configuration

**Key features:**
- Rolling updates cho zero-downtime deployment
- Resource requests/limits
- Health checks (readiness/liveness probes)

### `service.yaml`
Kubernetes Service để **expose inference API**.

**Cấu hình:**
- **Type:** ClusterIP (internal) hoặc LoadBalancer (external)
- **Port:** 80 → 80
- **Selector:** Pods với label `app: forecast`

**Truy cập:**
- Internal: `http://retail-forecast-service.default.svc.cluster.local`
- External: Qua LoadBalancer IP (nếu type=LoadBalancer)

### `hpa.yaml`
Horizontal Pod Autoscaler cho **auto-scaling**.

**Cấu hình:**
- **Min replicas:** 2
- **Max replicas:** 10
- **Target CPU:** 70%
- **Scale up/down:** Dựa trên CPU utilization

**Hoạt động:**
- Tự động tăng pods khi traffic cao
- Tự động giảm pods khi traffic thấp
- Đảm bảo cost optimization

---

## 📊 Monitoring Setup (`monitor/`)

### `alerts.bicep`
Application Insights alerts cho **production monitoring**.

**Alerts được tạo:**

1. **P95 Latency Alert** (`ai-p95-latency-high`)
   - **Trigger:** Response time > 400ms (P95)
   - **Evaluation:** Mỗi 1 phút, window 5 phút
   - **Severity:** Warning (2)
   - **Auto-mitigate:** Có

2. **Error Rate Alert** (`ai-5xx-rate-high`)
   - **Trigger:** Có failed requests (5xx errors)
   - **Evaluation:** Mỗi 1 phút, window 5 phút  
   - **Severity:** Warning (2)
   - **Auto-mitigate:** Có

**Deploy alerts:**
```bash
# Cần Application Insights resource ID từ main.bicep output
APP_INSIGHTS_ID="/subscriptions/{subscription-id}/resourceGroups/rg-mlops/providers/Microsoft.Insights/components/{app-insights-name}"

az deployment group create \
  --resource-group rg-mlops \
  --template-file monitor/alerts.bicep \
  --parameters appInsightsId="$APP_INSIGHTS_ID"
```

### `kql/error.kql`
KQL query để **theo dõi errors và failed requests**.

**Chức năng:**
- Filter requests với `success == false` hoặc `resultCode >= 500`
- Group by 5-minute bins, result code, operation name
- Đếm số lượng failures theo thời gian

**Sử dụng:**
1. Vào Azure Portal → Application Insights → Logs
2. Copy paste nội dung file `error.kql`
3. Run query để xem error trends

### `kql/latency.kql`
KQL query để **theo dõi response time metrics**.

**Chức năng:**
- Tính p50, p95, p99 percentiles của response duration
- Group by 5-minute bins và cloud role name
- Theo dõi performance trends theo thời gian

**Sử dụng:**
1. Vào Azure Portal → Application Insights → Logs
2. Copy paste nội dung file `latency.kql`
3. Run query để xem latency metrics

---

## 🔄 CI/CD Pipeline (`azure-pipelines.yml`)

Azure DevOps pipeline cho **automated build & deploy**.

### Pipeline Stages:

1. **Build Stage**
   - Build Docker images từ `train.Dockerfile` và `infer.Dockerfile`
   - Tag images với Build ID
   - Push images lên Azure Container Registry

### Pipeline Variables:
```yaml
variables:
  ACR_NAME: 'acrmlretail'
  # Có thể add thêm:
  # RESOURCE_GROUP: 'rg-mlops'
  # AKS_CLUSTER: 'aks-mlops-prod'
```

### Trigger:
- Tự động trigger khi có code push vào `main` branch
- Manual trigger từ Azure DevOps portal

**Setup Pipeline:**
1. Import repo vào Azure DevOps
2. Create new pipeline từ `azure-pipelines.yml`
3. Configure service connections cho ACR và AKS
4. Run pipeline

---

## 🚀 Complete Deployment Workflow

### 1. Infrastructure Setup
```bash
# Deploy hạ tầng
az deployment group create \
  --resource-group rg-mlops \
  --template-file infra/main.bicep

# Get AKS credentials
az aks get-credentials \
  --resource-group rg-mlops \
  --name aks-mlops-prod
```

### 2. Build & Push Images
```bash
# Login vào ACR
az acr login --name acrmlretail

# Build và push images
docker build -f aml/train.Dockerfile -t acrmlretail.azurecr.io/train:latest .
docker build -f aml/infer.Dockerfile -t acrmlretail.azurecr.io/infer:latest .

docker push acrmlretail.azurecr.io/train:latest
docker push acrmlretail.azurecr.io/infer:latest
```

### 3. ML Training
```bash
# Submit training job
az ml job create \
  --file aml/train-job.yml \
  --resource-group rg-mlops \
  --workspace-name mlw-retail
```

### 4. Kubernetes Deployment
```bash
# Deploy inference API
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Check status
kubectl get pods,svc,hpa
```

### 5. Monitoring Setup
```bash
# Deploy alerts
az deployment group create \
  --resource-group rg-mlops \
  --template-file monitor/alerts.bicep \
  --parameters appInsightsId="<APP_INSIGHTS_RESOURCE_ID>"
```

---

## 🔧 Troubleshooting

### Common Issues:

1. **ACR Authentication**
   ```bash
   # Attach ACR to AKS
   az aks update -n aks-mlops-prod -g rg-mlops --attach-acr acrmlretail
   ```

2. **Pod Image Pull Errors**
   ```bash
   # Check ACR permissions
   kubectl describe pod <pod-name>
   ```

3. **HPA Not Scaling**
   ```bash
   # Check metrics server
   kubectl top nodes
   kubectl top pods
   ```

4. **Application Insights Not Logging**
   - Kiểm tra APPLICATIONINSIGHTS_CONNECTION_STRING trong deployment
   - Verify Application Insights instrumentation key

---

## 📝 Environment Variables

### Required for Deployment:
```bash
# Azure Authentication
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_TENANT_ID=<your-tenant-id>

# Resource Configuration  
RESOURCE_GROUP=rg-mlops
ACR_NAME=acrmlretail
AKS_CLUSTER=aks-mlops-prod
AML_WORKSPACE=mlw-retail

# Application Insights (for monitoring)
APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string>
```

### Optional for Development:
```bash
# Local development
MODEL_PATH=/app/model
DEBUG=true
LOG_LEVEL=INFO
```

---

## 📚 Tài liệu tham khảo

- [Azure Machine Learning Documentation](https://docs.microsoft.com/en-us/azure/machine-learning/)
- [Azure Kubernetes Service Documentation](https://docs.microsoft.com/en-us/azure/aks/)
- [Azure Bicep Documentation](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [Application Insights KQL Reference](https://docs.microsoft.com/en-us/azure/azure-monitor/logs/kql-quick-reference)
