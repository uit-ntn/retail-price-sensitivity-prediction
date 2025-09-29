# AWS MLOps Setup - Retail Forecast

Thư mục này chứa toàn bộ **AWS cloud infrastructure** và **automation scripts** cho **Retail Forecast MLOps pipeline**.

---

## 📁 Cấu trúc tổng quan

```
aws/
├── infra/                    # 🏗️ Infrastructure as Code (Terraform)
│   ├── modules/             # Reusable Terraform modules
│   ├── envs/               # Environment-specific configurations
│   ├── main.tf             # Root infrastructure resources
│   ├── Makefile            # Infrastructure automation commands
│   └── README.md           # 📖 Infrastructure setup guide
│
├── k8s/                     # ☸️ Kubernetes Manifests & Add-ons
│   ├── addons/             # Cluster add-ons (metrics, autoscaler, ALB)
│   ├── ingress/            # ALB ingress configurations
│   ├── rbac/               # Role-based access control
│   ├── pdb/                # Pod disruption budgets
│   ├── kustomization.yaml  # Kustomize configuration
│   └── README.MD           # 📖 Kubernetes deployment guide
│
├── observability/          # 📊 Monitoring & Logging
│   ├── cloudwatch-alarms/ # CloudWatch alarms (Terraform)
│   ├── cloudwatch-logs/   # Fluent Bit logging setup
│   └── README.MD           # 📖 Observability setup guide
│
├── script/                 # 🚀 Automation Scripts
│   ├── pipelines/          # SageMaker ML pipelines
│   ├── monitoring/         # Model monitoring scripts
│   ├── *.py               # SageMaker automation scripts
│   ├── ecr_build_push.sh  # Container build & push
│   └── README.MD           # 📖 Scripts usage guide
│
├── Jenkinsfile             # 🔄 Jenkins CI/CD pipeline
├── .travis.yml             # 🔄 Travis CI pipeline (alternative)
└── README.md               # 📖 File này
```

---

## 🎯 Quick Start Guide

### 1. **Infrastructure Setup** → [`infra/`](./infra/)
Deploy AWS infrastructure với Terraform:

```bash
# Navigate to infra directory
cd infra

# Deploy development environment
make init ENV=dev
make plan ENV=dev
make apply ENV=dev
```

**Resources được tạo:**
- VPC với public/private subnets
- EKS cluster với managed node groups
- ECR repositories cho Docker images
- S3 buckets cho data và artifacts
- IAM roles và policies
- KMS keys cho encryption
- CloudTrail cho audit logging

### 2. **Kubernetes Setup** → [`k8s/`](./k8s/)
Deploy Kubernetes add-ons và application:

```bash
# Navigate to k8s directory
cd k8s

# Deploy all manifests với Kustomize
kubectl apply -k .

# Or deploy individually
kubectl apply -f addons/
kubectl apply -f ingress/
kubectl apply -f rbac/
```

**Components được deploy:**
- Metrics Server cho resource monitoring
- Cluster Autoscaler cho node scaling
- AWS Load Balancer Controller cho ALB
- ExternalDNS cho automatic DNS
- Pod security standards
- RBAC configurations

### 3. **Observability Setup** → [`observability/`](./observability/)
Setup monitoring và logging:

```bash
# Navigate to observability directory
cd observability

# Deploy CloudWatch alarms
cd cloudwatch-alarms
terraform apply

# Deploy Fluent Bit logging
cd ../cloudwatch-logs
kubectl apply -f fluent-bit-daemonset.yaml
```

**Monitoring được setup:**
- ALB 5xx error alarms
- EKS high CPU alarms
- Container log collection với Fluent Bit
- CloudWatch Logs integration

### 4. **ML Pipeline Automation** → [`script/`](./script/)
Run SageMaker ML workflows:

```bash
# Navigate to script directory
cd script

# Complete training pipeline
python create_training_job.py
python register_model.py
python deploy_endpoint.py
python autoscaling_endpoint.py

# Or use SageMaker Pipelines
python pipelines/sagemaker_pipeline.py
```

**ML Operations:**
- SageMaker training jobs
- Model registry management
- Endpoint deployment và scaling
- Model monitoring setup
- Container build và push

---

## 🔄 CI/CD Pipelines

### Jenkins Pipeline (`Jenkinsfile`)
**5-stage automated pipeline:**

1. **Setup** - Environment preparation
2. **Test** - Code quality và unit tests
3. **Train** - SageMaker training job
4. **Register** - Model registry registration
5. **Deploy** - Endpoint deployment

**Usage:**
```bash
# Setup Jenkins với AWS credentials
# Import Jenkinsfile vào Jenkins pipeline
# Configure environment variables
# Run pipeline
```

### Travis CI Pipeline (`.travis.yml`)
**Alternative CI/CD** cho GitHub integration:

**Features:**
- Automatic trigger trên code push
- Python environment setup
- SageMaker workflow execution
- Environment variable management

---

## 🏗️ Architecture Overview

### **Infrastructure Layer** (`infra/`)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   VPC Network   │    │   EKS Cluster   │    │  ECR Registry   │
│                 │    │                 │    │                 │
│ • Public Subnets│    │ • Control Plane │    │ • Train Images  │
│ • Private Subnets│   │ • Worker Nodes  │    │ • Infer Images  │
│ • NAT Gateways  │    │ • Add-ons       │    │ • Lifecycle     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
        ┌─────────────────────────────────────────────────┐
        │              S3 Storage & IAM                   │
        │                                                 │
        │ • Data Bucket     • Artifacts Bucket           │
        │ • IAM Roles       • Service Accounts           │
        │ • KMS Keys        • CloudTrail Logs            │
        └─────────────────────────────────────────────────┘
```

### **Application Layer** (`k8s/`)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Load Balancer  │    │   Application   │    │   Monitoring    │
│                 │    │                 │    │                 │
│ • ALB Ingress   │    │ • Inference API │    │ • Metrics Server│
│ • SSL Termination│   │ • HPA Scaling   │    │ • Fluent Bit    │
│ • ExternalDNS   │    │ • Pod Security  │    │ • CloudWatch    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **ML Operations Layer** (`script/`)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Training      │    │ Model Registry  │    │   Inference     │
│                 │    │                 │    │                 │
│ • SageMaker Jobs│    │ • Versioning    │    │ • Endpoints     │
│ • Data Processing│   │ • Approval      │    │ • Auto-scaling  │
│ • Model Artifacts│   │ • Metadata      │    │ • Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 📊 Component Matrix

| Component | Purpose | Technology | Status |
|-----------|---------|------------|--------|
| **VPC** | Network isolation | Terraform | ✅ Ready |
| **EKS** | Kubernetes cluster | Terraform + kubectl | ✅ Ready |
| **ECR** | Container registry | Terraform | ⚠️ Needs setup |
| **S3** | Data/artifact storage | Terraform | ✅ Ready |
| **ALB** | Load balancing | Kubernetes Ingress | ✅ Ready |
| **SageMaker** | ML training/inference | Python Scripts | ✅ Ready |
| **CloudWatch** | Monitoring/logging | Terraform + Fluent Bit | ✅ Ready |
| **IAM** | Access control | Terraform + IRSA | ✅ Ready |

---

## 🚀 Deployment Scenarios

### **Scenario 1: Complete Fresh Setup**
```bash
# 1. Infrastructure
cd infra && make apply ENV=dev

# 2. Kubernetes
cd ../k8s && kubectl apply -k .

# 3. Observability
cd ../observability && terraform apply

# 4. ML Pipeline
cd ../script && python pipelines/sagemaker_pipeline.py
```

### **Scenario 2: Code Update Only**
```bash
# 1. Build & push new image
cd script
./ecr_build_push.sh $ECR_REPO_URI

# 2. Update Kubernetes deployment
kubectl set image deployment/retail-server \
  retail-server=$ECR_REPO_URI:latest -n retail

# 3. Retrain model (if needed)
python create_training_job.py
```

### **Scenario 3: Infrastructure Update**
```bash
# 1. Plan changes
cd infra && make plan ENV=dev

# 2. Apply changes
make apply ENV=dev

# 3. Update kubeconfig
aws eks update-kubeconfig --name retail-mlops-dev
```

---

## 🔧 Environment Configuration

### **Required Environment Variables:**
```bash
# AWS Configuration
export AWS_REGION="ap-southeast-1"
export AWS_ACCOUNT_ID="123456789012"

# Infrastructure
export TF_VAR_account_id="123456789012"
export TF_VAR_region="ap-southeast-1"

# SageMaker
export SM_EXEC_ROLE_ARN="arn:aws:iam::123456:role/sagemaker-exec-role"
export S3_DATA_BUCKET="retail-mlops-data-123456-ap-southeast-1"
export S3_ARTIFACTS_BUCKET="retail-mlops-artifacts-123456-ap-southeast-1"

# Kubernetes
export CLUSTER_NAME="retail-mlops-dev"
export DOMAIN="your-domain.com"
```

### **Configuration Files:**
- `infra/envs/dev/terraform.tfvars` - Infrastructure variables
- `k8s/kustomization.yaml` - Kubernetes resources
- `script/pipelines/params.json` - ML pipeline parameters

---

## 🔍 Monitoring & Troubleshooting

### **Health Checks:**
```bash
# Infrastructure
terraform show | grep -E "(vpc|eks|s3)"

# Kubernetes
kubectl get nodes
kubectl get pods --all-namespaces

# SageMaker
aws sagemaker list-training-jobs --max-results 5
aws sagemaker list-endpoints
```

### **Common Issues & Solutions:**

#### **🚨 EKS Access Denied**
```bash
# Update kubeconfig
aws eks update-kubeconfig --name retail-mlops-dev

# Check IAM permissions
aws sts get-caller-identity
```

#### **🚨 SageMaker Training Failed**
```bash
# Check logs
aws logs describe-log-streams --log-group-name /aws/sagemaker/TrainingJobs

# Check role permissions
aws iam get-role --role-name sagemaker-exec-role
```

#### **🚨 ALB Not Creating**
```bash
# Check AWS Load Balancer Controller
kubectl logs -f deployment/aws-load-balancer-controller -n kube-system

# Check service account annotations
kubectl get sa aws-load-balancer-controller -n kube-system -o yaml
```

---

## 💰 Cost Management

### **Cost Optimization Tips:**

1. **EKS Cluster**
   - Use spot instances cho worker nodes
   - Scale down during off-hours
   - Right-size instance types

2. **SageMaker**
   - Use spot training instances
   - Stop endpoints khi không dùng
   - Optimize instance types

3. **Storage**
   - Set S3 lifecycle policies
   - Use Intelligent Tiering
   - Clean up old artifacts

4. **Logging**
   - Set CloudWatch log retention
   - Use log filtering
   - Monitor log volume

### **Cost Monitoring:**
```bash
# Check current costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

---

## 📚 Additional Resources

### **Documentation Links:**
- [Infrastructure Setup Guide](./infra/README.md)
- [Kubernetes Deployment Guide](./k8s/README.MD)
- [Observability Setup Guide](./observability/README.MD)
- [Scripts Usage Guide](./script/README.MD)

### **External References:**
- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [SageMaker MLOps Guide](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-projects.html)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

---

## 🤝 Contributing

### **Development Workflow:**
1. Create feature branch
2. Update relevant README files
3. Test infrastructure changes
4. Submit pull request
5. Code review và approval

### **File Organization:**
- Keep component-specific docs trong từng thư mục
- Update main README khi thêm components mới
- Include troubleshooting sections
- Provide working examples

---

**🎯 Ready to deploy? Start with [`infra/README.md`](./infra/README.md) for infrastructure setup!**
