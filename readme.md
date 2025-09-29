# Retail Forecast MLOps (Azure + AWS)

Dự án demo **MLOps pipeline đa cloud (Azure & AWS)** cho bài toán **dự báo nhu cầu bán lẻ**.  
Ngôn ngữ: **Python**, hạ tầng bằng **Terraform / Bicep**, triển khai inference bằng **Kubernetes (AKS/EKS)**,  
CI/CD bằng **Azure DevOps Pipeline** hoặc **Jenkins/Travis CI**.

---

## 🎯 Mục tiêu
- Huấn luyện mô hình dự báo nhu cầu sử dụng SageMaker hoặc Azure ML.
- Tự động build & deploy container model API lên cloud.
- CI/CD cho ML pipeline: build → test → train → register → deploy.
- So sánh triển khai trên **Azure (AML + AKS)** và **AWS (SageMaker + EKS)**.
- Expose API backend (FastAPI) cho ứng dụng khác sử dụng.

---

## 📂 Cấu trúc repo

```
retail-forecast/
├─ core/                 # Dependencies chung cho ML
│   └─ requirements.txt  # numpy, pandas, scikit-learn, mlflow, fastapi, pytest
│
├─ server/               # Backend inference API (FastAPI)
│   ├─ DockerFile        # Container definition cho inference API
│   ├─ Readme.md         # Hướng dẫn setup server
│   └─ requirements.txt  # Dependencies cho API server
│
├─ azure/                # 🔵 Azure MLOps Configuration
│   ├─ aml/              # Azure Machine Learning
│   │   ├─ train.Dockerfile      # Training container image
│   │   ├─ infer.Dockerfile      # Inference container image
│   │   ├─ train-job.yml         # AML training job definition
│   │   ├─ deployment/           # Online endpoint configs
│   │   │   ├─ endpoint.yml      # Managed online endpoint
│   │   │   └─ blue.yml          # Blue deployment config
│   │   ├─ environments/         # ML environments
│   │   │   └─ conda.yml         # Conda environment
│   │   └─ README.MD             # 📖 Azure ML documentation
│   │
│   ├─ infra/            # Infrastructure as Code
│   │   ├─ main.tf               # Terraform configuration
│   │   ├─ online_endpoint.tf    # Azure ML endpoint (AzAPI)
│   │   ├─ alerts.tf             # Application Insights alerts
│   │   ├─ main.bicep            # Bicep alternative
│   │   ├─ dev.tfvars            # Development variables
│   │   ├─ prod.tfvars           # Production variables
│   │   ├─ parameters/           # Bicep parameter files
│   │   └─ README.MD             # 📖 Infrastructure documentation
│   │
│   ├─ k8s/              # Kubernetes manifests cho AKS
│   │   ├─ deployment.yaml       # Pod deployment
│   │   ├─ service.yaml          # Service exposure
│   │   ├─ hpa.yaml             # Horizontal Pod Autoscaler
│   │   └─ README.MD             # 📖 Kubernetes documentation
│   │
│   ├─ monitor/          # Monitoring & Observability
│   │   ├─ alerts.bicep          # Application Insights alerts
│   │   ├─ kql/                  # KQL queries
│   │   │   ├─ error.kql         # Error tracking queries
│   │   │   └─ latency.kql       # Latency monitoring queries
│   │   └─ README.MD             # 📖 Monitoring documentation
│   │
│   ├─ azure-pipelines.yml       # Azure DevOps CI/CD
│   └─ README.md                 # 📖 Azure setup overview
│
├─ aws/                  # 🟠 AWS MLOps Configuration
│   ├─ infra/            # Terraform infrastructure
│   │   ├─ modules/              # Reusable Terraform modules
│   │   │   ├─ vpc/              # VPC networking
│   │   │   ├─ eks/              # EKS cluster
│   │   │   ├─ ecr/              # Container registry
│   │   │   ├─ s3/               # Storage buckets
│   │   │   ├─ iam-irsa/         # IAM roles for service accounts
│   │   │   ├─ kms/              # Encryption keys
│   │   │   └─ cloudtrail/       # Audit logging
│   │   ├─ envs/                 # Environment configurations
│   │   │   └─ dev/              # Development environment
│   │   ├─ main.tf               # Root infrastructure
│   │   ├─ Makefile              # Infrastructure automation
│   │   └─ README.md             # 📖 Infrastructure documentation
│   │
│   ├─ k8s/              # Kubernetes manifests cho EKS
│   │   ├─ addons/               # Cluster add-ons
│   │   │   ├─ metrics-server.yaml
│   │   │   ├─ cluster-autoscaler.yaml
│   │   │   ├─ aws-load-balancer-controller.yaml
│   │   │   ├─ external-dns.yaml
│   │   │   └─ secrets-store-csi/
│   │   ├─ ingress/              # Ingress configurations
│   │   │   └─ alb-ingress.yaml
│   │   ├─ rbac/                 # Role-based access control
│   │   ├─ pdb/                  # Pod disruption budgets
│   │   ├─ namespace.yaml        # Namespace definition
│   │   ├─ service.yaml          # Service exposure
│   │   ├─ hpa.yaml             # Horizontal Pod Autoscaler
│   │   ├─ kustomization.yaml    # Kustomize configuration
│   │   └─ README.MD             # 📖 Kubernetes documentation
│   │
│   ├─ observability/    # Monitoring & Logging
│   │   ├─ cloudwatch-alarms/    # CloudWatch alerts
│   │   │   └─ alarms.tf
│   │   ├─ cloudwatch-logs/      # Log collection
│   │   │   └─ fluent-bit-daemonset.yaml
│   │   └─ README.MD             # 📖 Observability documentation
│   │
│   ├─ script/           # SageMaker automation scripts
│   │   ├─ pipelines/            # ML pipelines
│   │   │   ├─ sagemaker_pipeline.py
│   │   │   └─ params.json
│   │   ├─ monitoring/           # Model monitoring
│   │   │   ├─ data_quality_baseline.py
│   │   │   ├─ schedule_data_quality_monitor.py
│   │   │   └─ schedule_model_quality_monitor.py
│   │   ├─ create_training_job.py
│   │   ├─ register_model.py
│   │   ├─ deploy_endpoint.py
│   │   ├─ autoscaling_endpoint.py
│   │   ├─ processing_evaluate.py
│   │   ├─ ecr_build_push.sh
│   │   └─ README.MD             # 📖 Scripts documentation
│   │
│   ├─ Jenkinsfile       # Jenkins CI/CD pipeline
│   ├─ .travis.yml       # Travis CI pipeline
│   └─ README.md         # 📖 AWS setup overview
│
├─ tests/                # Test directory (cần implement)
├─ .gitignore           # Git ignore với security best practices
└─ README.md            # 📖 File này
```

---

## 🚀 Quick Start Guide

### 🔵 Azure Deployment

#### 1. **Infrastructure Setup** → [`azure/infra/`](./azure/infra/)
```bash
cd azure/infra

# Deploy với Terraform
terraform init
terraform plan -var-file="dev.tfvars"
terraform apply -var-file="dev.tfvars"

# Hoặc deploy với Bicep
az deployment group create \
  --resource-group rg-mlops \
  --template-file main.bicep
```

#### 2. **ML Training & Deployment** → [`azure/aml/`](./azure/aml/)
```bash
cd azure/aml

# Build và push containers
docker build -f train.Dockerfile -t acrretaildev.azurecr.io/retail/train:latest .
docker build -f infer.Dockerfile -t acrretaildev.azurecr.io/retail/infer:latest .

# Submit training job
az ml job create --file train-job.yml

# Deploy online endpoint
az ml online-endpoint create --file deployment/endpoint.yml
az ml online-deployment create --file deployment/blue.yml --all-traffic
```

#### 3. **Kubernetes Deployment** → [`azure/k8s/`](./azure/k8s/)
```bash
cd azure/k8s

# Get AKS credentials
az aks get-credentials --resource-group rg-mlops --name aks-mlops-prod

# Deploy application
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
```

#### 4. **Monitoring Setup** → [`azure/monitor/`](./azure/monitor/)
```bash
cd azure/monitor

# Deploy alerts
az deployment group create \
  --resource-group rg-mlops \
  --template-file alerts.bicep \
  --parameters appInsightsId="<APP_INSIGHTS_ID>"
```

### 🟠 AWS Deployment

#### 1. **Infrastructure Setup** → [`aws/infra/`](./aws/infra/)
```bash
cd aws/infra

# Deploy development environment
make init ENV=dev
make plan ENV=dev
make apply ENV=dev
```

#### 2. **Kubernetes Setup** → [`aws/k8s/`](./aws/k8s/)
```bash
cd aws/k8s

# Deploy all manifests với Kustomize
kubectl apply -k .

# Or deploy individually
kubectl apply -f addons/
kubectl apply -f ingress/
kubectl apply -f rbac/
```

#### 3. **ML Pipeline Automation** → [`aws/script/`](./aws/script/)
```bash
cd aws/script

# Complete training pipeline
python create_training_job.py
python register_model.py
python deploy_endpoint.py
python autoscaling_endpoint.py

# Or use SageMaker Pipelines
python pipelines/sagemaker_pipeline.py
```

#### 4. **Observability Setup** → [`aws/observability/`](./aws/observability/)
```bash
cd aws/observability

# Deploy CloudWatch alarms
cd cloudwatch-alarms && terraform apply

# Deploy Fluent Bit logging
cd ../cloudwatch-logs && kubectl apply -f fluent-bit-daemonset.yaml
```

---

## 🔄 CI/CD Pipelines

### Azure DevOps Pipeline
- **File:** `azure/azure-pipelines.yml`
- **Features:** Build Docker images, push to ACR, deploy to AKS
- **Trigger:** Code push to main branch

### Jenkins Pipeline (AWS)
- **File:** `aws/Jenkinsfile`
- **Stages:** Setup → Test → Train → Register → Deploy
- **Features:** SageMaker integration, automated MLOps workflow

### Travis CI (AWS Alternative)
- **File:** `aws/.travis.yml`
- **Features:** Lightweight CI/CD cho GitHub integration

---

## 🏗️ Architecture Comparison

| Component | Azure | AWS |
|-----------|-------|-----|
| **Infrastructure** | Terraform + Bicep | Terraform |
| **ML Platform** | Azure ML Workspace | SageMaker |
| **Training** | AML Training Jobs | SageMaker Training Jobs |
| **Model Registry** | AML Model Registry | SageMaker Model Registry |
| **Inference** | AML Online Endpoints + AKS | SageMaker Endpoints + EKS |
| **Container Registry** | ACR | ECR |
| **Kubernetes** | AKS | EKS |
| **Monitoring** | Application Insights + KQL | CloudWatch + Fluent Bit |
| **CI/CD** | Azure DevOps | Jenkins / Travis CI |
| **Storage** | Azure Storage | S3 |
| **Networking** | VNet + Application Gateway | VPC + ALB |

---

## 📊 Feature Matrix

### ✅ **Implemented Features**

#### Azure:
- [x] Complete Terraform infrastructure
- [x] Azure ML training pipeline
- [x] Online endpoint deployment
- [x] AKS deployment manifests
- [x] Application Insights monitoring
- [x] KQL queries for observability
- [x] Blue-green deployment support
- [x] Auto-scaling configuration

#### AWS:
- [x] Modular Terraform infrastructure
- [x] SageMaker training automation
- [x] Model registry integration
- [x] EKS cluster with add-ons
- [x] CloudWatch monitoring
- [x] Fluent Bit log collection
- [x] Jenkins/Travis CI pipelines
- [x] Container build automation

### 🔧 **Cần hoàn thiện**

#### Common:
- [ ] Core ML training code (`core/src/train.py`)
- [ ] FastAPI server implementation (`server/app.py`)
- [ ] Test suite implementation (`tests/`)
- [ ] Sample data và notebooks

#### Azure Specific:
- [ ] AKS ingress với Application Gateway
- [ ] Azure Key Vault integration
- [ ] Cost management alerts

#### AWS Specific:
- [ ] ECR repository setup trong Terraform
- [ ] EKS deployment manifest
- [ ] VPC endpoints configuration

---

## 🔒 Security Features

### **Implemented:**
- [x] Comprehensive `.gitignore` với security patterns
- [x] IAM roles và RBAC configurations
- [x] Private container registries
- [x] Secrets management (Key Vault/Secrets Manager)
- [x] Network security groups/policies
- [x] Encryption at rest và in transit

### **Best Practices:**
- [x] Least privilege access
- [x] Service accounts với minimal permissions
- [x] Private subnets cho worker nodes
- [x] SSL/TLS termination
- [x] Audit logging enabled

---

## 💰 Cost Optimization

### **Azure:**
- Scale-to-zero compute clusters
- Standard ACR SKU cho dev
- 30-day log retention
- Spot instances support

### **AWS:**
- Auto-scaling EKS node groups
- Spot instances cho training
- S3 lifecycle policies
- CloudWatch log retention policies

---

## 📚 Documentation

### **Comprehensive Guides:**
- [📖 Azure Setup Overview](./azure/README.md)
- [📖 Azure Infrastructure Guide](./azure/infra/README.MD)
- [📖 Azure ML Guide](./azure/aml/README.MD)
- [📖 Azure Kubernetes Guide](./azure/k8s/README.MD)
- [📖 Azure Monitoring Guide](./azure/monitor/README.MD)
- [📖 AWS Setup Overview](./aws/README.md)
- [📖 AWS Infrastructure Guide](./aws/infra/README.md)
- [📖 AWS Kubernetes Guide](./aws/k8s/README.MD)
- [📖 AWS Observability Guide](./aws/observability/README.MD)
- [📖 AWS Scripts Guide](./aws/script/README.MD)

### **Quick References:**
- Environment variables setup
- Deployment workflows
- Troubleshooting guides
- Cost optimization tips

---

## 🚀 Getting Started

### **Choose Your Cloud:**

#### 🔵 **Start with Azure:**
```bash
git clone <repo-url>
cd retail-forecast/azure
# Follow azure/README.md
```

#### 🟠 **Start with AWS:**
```bash
git clone <repo-url>
cd retail-forecast/aws
# Follow aws/README.md
```

#### 🔄 **Multi-Cloud Setup:**
```bash
# Deploy both platforms
cd retail-forecast
# Setup Azure first
cd azure && # follow setup
# Setup AWS second  
cd ../aws && # follow setup
```

---

## 🤝 Contributing

### **Development Workflow:**
1. Fork repository
2. Create feature branch
3. Update relevant README files
4. Test infrastructure changes
5. Submit pull request

### **Documentation Standards:**
- Keep component-specific docs trong từng thư mục
- Update main README khi thêm major features
- Include troubleshooting sections
- Provide working examples

---

## 📝 Environment Variables

### **Required for Azure:**
```bash
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_TENANT_ID="your-tenant-id"
export RESOURCE_GROUP="rg-mlops"
export ACR_NAME="acrmlretail"
export AKS_CLUSTER="aks-mlops-prod"
```

### **Required for AWS:**
```bash
export AWS_REGION="ap-southeast-1"
export AWS_ACCOUNT_ID="123456789012"
export CLUSTER_NAME="retail-mlops-dev"
export S3_DATA_BUCKET="retail-mlops-data-123456-ap-southeast-1"
```

---

## 📞 Support & Resources

### **External Documentation:**
- [Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/)
- [Amazon SageMaker](https://docs.aws.amazon.com/sagemaker/)
- [Terraform](https://www.terraform.io/docs/)
- [Kubernetes](https://kubernetes.io/docs/)

### **Community:**
- Issues: Report bugs và feature requests
- Discussions: Architecture questions và best practices
- Wiki: Additional examples và tutorials

---

**🎯 Ready to start? Choose your cloud platform và follow the respective README guide!**