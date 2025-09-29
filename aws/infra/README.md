# AWS Infrastructure - Retail Forecast MLOps

Thư mục này chứa **Infrastructure as Code (IaC)** sử dụng **Terraform** để triển khai toàn bộ hạ tầng AWS cho Retail Forecast MLOps pipeline.

---

## 📁 Cấu trúc thư mục

```
infra/
├── envs/                   # Environment-specific configurations
│   └── dev/               # Development environment
│       ├── main.tf        # Environment-specific resources
│       ├── variables.tf   # Environment variables
│       ├── backend.tf     # Terraform state backend
│       ├── outs.tf        # Environment outputs
│       └── terraform.tfvars.example
│
├── modules/               # Reusable Terraform modules
│   ├── vpc/              # VPC networking module
│   ├── eks/              # EKS cluster module
│   ├── ecr/              # ECR repositories module
│   ├── s3/               # S3 buckets module
│   ├── iam-irsa/         # IAM roles for service accounts
│   ├── kms/              # KMS encryption keys
│   └── cloudtrail/       # CloudTrail logging
│
├── main.tf               # Root module resources
├── variables.tf          # Root module variables
├── output.tf             # Root module outputs
├── Makefile              # Infrastructure automation commands
└── README.md             # File này
```

---

## 🏗️ Root Module (`main.tf`)

### Resources được tạo:

1. **S3 Buckets**
   - `retail-mlops-data-{account_id}-{region}` - Lưu training data
   - `retail-mlops-artifacts-{account_id}-{region}` - Lưu model artifacts

2. **IAM Role**
   - `sagemaker-exec-role` - Execution role cho SageMaker jobs
   - Policy: `AmazonSageMakerFullAccess`

### Provider Configuration:
- **Region:** `ap-southeast-1` (Singapore)
- **Account ID:** Từ variable `var.account_id`

---

## 📦 Terraform Modules (`modules/`)

### `vpc/` - Virtual Private Cloud
**Chức năng:**
- Tạo VPC với public/private subnets
- Internet Gateway và NAT Gateways
- Route tables và security groups
- VPC endpoints cho AWS services

**Resources:**
- VPC với CIDR block tùy chỉnh
- 3 Availability Zones cho high availability
- Public subnets cho Load Balancers
- Private subnets cho EKS worker nodes

### `eks/` - Elastic Kubernetes Service
**Chức năng:**
- EKS cluster với managed node groups
- IRSA (IAM Roles for Service Accounts)
- Add-ons: VPC CNI, CoreDNS, kube-proxy
- Security groups và networking

**Features:**
- Kubernetes version 1.28+
- Managed node groups với auto-scaling
- Spot instances support
- Private cluster endpoints

### `ecr/` - Elastic Container Registry
**Chức năng:**
- ECR repositories cho Docker images
- Lifecycle policies cho image cleanup
- Cross-region replication (optional)
- Image scanning security

**Repositories:**
- `retail-forecast-train` - Training images
- `retail-forecast-infer` - Inference images

### `s3/` - Simple Storage Service
**Chức năng:**
- S3 buckets với versioning
- Encryption at rest (KMS)
- Lifecycle policies
- Cross-region replication

**Buckets:**
- Data bucket - Training datasets
- Artifacts bucket - Model artifacts
- Logs bucket - Application logs

### `iam-irsa/` - IAM Roles for Service Accounts
**Chức năng:**
- OIDC provider cho EKS
- IAM roles với trust policy
- Service account bindings
- Fine-grained permissions

**Roles:**
- `eks-cluster-autoscaler-role`
- `aws-load-balancer-controller-role`
- `external-dns-role`
- `fluent-bit-role`

### `kms/` - Key Management Service
**Chức năng:**
- KMS keys cho encryption
- Key policies và aliases
- Cross-service encryption
- Key rotation

**Keys:**
- EKS cluster encryption key
- S3 bucket encryption key
- CloudWatch logs encryption key

### `cloudtrail/` - AWS CloudTrail
**Chức năng:**
- API call logging
- S3 bucket for trail storage
- CloudWatch Logs integration
- Multi-region trail

**Features:**
- Data events logging
- Management events logging
- Insight events (optional)

---

## 🌍 Environment Management (`envs/`)

### Development Environment (`envs/dev/`)

#### `main.tf`
Environment-specific resource configurations:
```hcl
module "vpc" {
  source = "../../modules/vpc"
  
  vpc_cidr = "10.0.0.0/16"
  environment = "dev"
  # ... other configs
}

module "eks" {
  source = "../../modules/eks"
  
  cluster_name = "retail-mlops-dev"
  node_group_instance_types = ["t3.medium"]
  # ... other configs
}
```

#### `variables.tf`
Environment variables:
```hcl
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}
```

#### `backend.tf`
Terraform state backend:
```hcl
terraform {
  backend "s3" {
    bucket = "terraform-state-retail-mlops"
    key    = "dev/terraform.tfstate"
    region = "ap-southeast-1"
    encrypt = true
  }
}
```

#### `terraform.tfvars.example`
Example environment values:
```hcl
account_id = "123456789012"
region     = "ap-southeast-1"
environment = "dev"
vpc_cidr   = "10.0.0.0/16"
```

---

## 🛠️ Makefile Commands

### Available Commands:

```bash
# Initialize Terraform
make init ENV=dev

# Plan infrastructure changes
make plan ENV=dev

# Apply infrastructure changes
make apply ENV=dev

# Destroy infrastructure
make destroy ENV=dev

# Format Terraform files
make fmt ENV=dev

# Validate Terraform configuration
make validate ENV=dev
```

### Usage Examples:

```bash
# Setup development environment
make init ENV=dev
make plan ENV=dev
make apply ENV=dev

# Format and validate code
make fmt ENV=dev
make validate ENV=dev

# Cleanup resources
make destroy ENV=dev
```

---

## 🚀 Deployment Workflow

### 1. Prerequisites
```bash
# Install required tools
brew install terraform awscli kubectl

# Configure AWS credentials
aws configure
# hoặc
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="ap-southeast-1"
```

### 2. Setup Terraform Backend
```bash
# Create S3 bucket for Terraform state
aws s3 mb s3://terraform-state-retail-mlops-$(aws sts get-caller-identity --query Account --output text)

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket terraform-state-retail-mlops-$(aws sts get-caller-identity --query Account --output text) \
  --versioning-configuration Status=Enabled
```

### 3. Configure Environment
```bash
cd envs/dev

# Copy example tfvars
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

### 4. Deploy Infrastructure
```bash
# Initialize and plan
make init ENV=dev
make plan ENV=dev

# Review plan output, then apply
make apply ENV=dev
```

### 5. Verify Deployment
```bash
# Check EKS cluster
aws eks describe-cluster --name retail-mlops-dev

# Update kubeconfig
aws eks update-kubeconfig --name retail-mlops-dev

# Verify nodes
kubectl get nodes
```

---

## 🔧 Configuration Variables

### Required Variables:
```hcl
account_id  = "123456789012"        # AWS Account ID
region      = "ap-southeast-1"      # AWS Region
environment = "dev"                 # Environment name
```

### Optional Variables:
```hcl
vpc_cidr                = "10.0.0.0/16"
eks_cluster_version     = "1.28"
node_group_instance_types = ["t3.medium", "t3.large"]
node_group_scaling_config = {
  desired_size = 2
  max_size     = 10
  min_size     = 1
}
```

---

## 📊 Outputs

### Infrastructure Outputs:
```hcl
# EKS Cluster
eks_cluster_id                = "retail-mlops-dev"
eks_cluster_arn              = "arn:aws:eks:..."
eks_cluster_endpoint         = "https://..."
eks_cluster_security_group_id = "sg-..."

# VPC
vpc_id              = "vpc-..."
private_subnet_ids  = ["subnet-...", "subnet-..."]
public_subnet_ids   = ["subnet-...", "subnet-..."]

# IAM
sagemaker_exec_role_arn = "arn:aws:iam::...role/sagemaker-exec-role"

# S3
data_bucket_name      = "retail-mlops-data-..."
artifacts_bucket_name = "retail-mlops-artifacts-..."
```

---

## 🔒 Security Best Practices

### 1. IAM Permissions
- Sử dụng least privilege principle
- IRSA cho Kubernetes service accounts
- Separate roles cho từng service

### 2. Network Security
- Private subnets cho worker nodes
- Security groups với restrictive rules
- VPC endpoints cho AWS services

### 3. Encryption
- KMS encryption cho EKS clusters
- S3 bucket encryption at rest
- CloudWatch logs encryption

### 4. Monitoring
- CloudTrail cho API logging
- VPC Flow Logs
- EKS control plane logging

---

## 🐛 Troubleshooting

### Common Issues:

1. **Terraform State Lock**
   ```bash
   # Force unlock if stuck
   terraform force-unlock LOCK_ID -force
   ```

2. **EKS Node Group Issues**
   ```bash
   # Check node group status
   aws eks describe-nodegroup --cluster-name retail-mlops-dev --nodegroup-name main
   
   # Check Auto Scaling Group
   aws autoscaling describe-auto-scaling-groups
   ```

3. **IAM Permission Errors**
   ```bash
   # Check current user permissions
   aws sts get-caller-identity
   aws iam get-user
   
   # Simulate policy
   aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::ACCOUNT:user/USERNAME --action-names eks:DescribeCluster
   ```

4. **S3 Bucket Name Conflicts**
   - S3 bucket names must be globally unique
   - Include account ID and region in bucket names
   - Check bucket exists: `aws s3 ls s3://bucket-name`

---

## 📚 Tài liệu tham khảo

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/) 