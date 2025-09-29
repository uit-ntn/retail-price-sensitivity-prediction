terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.31" }
    helm = { source = "hashicorp/helm", version = "~> 2.13" }
  }
}

provider "aws" {
  region = var.region
}

locals {
  name_prefix  = "${var.project}-${var.env}"
  tags = {
    Project = var.project
    Env     = var.env
    Owner   = "mlops"
    CostCenter = "ml"
  }
}

# --- VPC ---
module "vpc" {
  source = "../../modules/vpc"
  name_prefix = local.name_prefix
  az_count    = var.az_count
  allowed_cidrs = var.allowed_cidrs
  tags = local.tags
}

# --- KMS keys (S3/ECR/Logs) ---
module "kms" {
  source = "../../modules/kms"
  name_prefix = local.name_prefix
  tags = local.tags
}

# --- S3 buckets (data, artifacts) ---
module "s3" {
  source = "../../modules/s3"
  name_prefix = local.name_prefix
  kms_key_arn = module.kms.kms_key_arn
  tags = local.tags
}

# --- ECR repository for server image ---
module "ecr" {
  source = "../../modules/ecr"
  name_prefix = local.name_prefix
  image_mutability = "IMMUTABLE"
  scan_on_push     = true
  kms_key_arn      = module.kms.kms_key_arn
  tags = local.tags
}

# --- EKS cluster + managed nodegroups ---
module "eks" {
  source = "../../modules/eks"
  name_prefix     = local.name_prefix
  cluster_version = var.cluster_version
  vpc_id          = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  public_subnet_ids  = module.vpc.public_subnet_ids
  instance_types  = var.instance_types
  spot            = var.spot
  tags            = local.tags
}

# --- IRSA roles for controllers (ALB, external-dns, cluster-autoscaler, app S3) ---
module "iam_irsa" {
  source = "../../modules/iam-irsa"
  name_prefix     = local.name_prefix
  oidc_provider_arn = module.eks.oidc_provider_arn
  oidc_provider_url = module.eks.oidc_provider_url
  s3_bucket_arn     = module.s3.data_bucket_arn
  tags = local.tags
}

# --- CloudTrail (account-wide) ---
module "cloudtrail" {
  source      = "../../modules/cloudtrail"
  name_prefix = local.name_prefix
  kms_key_arn = module.kms.kms_key_arn
  tags        = local.tags
}

# ===== Kube providers wired to EKS =====
data "aws_eks_cluster" "this" {
  name = module.eks.cluster_name
}
data "aws_eks_cluster_auth" "this" {
  name = module.eks.cluster_name
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.this.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.this.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.this.token
}

provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.this.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.this.certificate_authority[0].data)
    token                  = data.aws_eks_cluster_auth.this.token
  }
}

# --- Optionally install metrics-server via Helm (quick) ---
resource "helm_release" "metrics_server" {
  name       = "metrics-server"
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  namespace  = "kube-system"
  version    = "3.12.1" # adjust as needed
  set {
    name  = "args"
    value = "{--kubelet-insecure-tls,--kubelet-preferred-address-types=InternalIP}"
  }
}

# Output IRSA ARNs for k8s manifests
output "irsa_alb_controller_role_arn"    { value = module.iam_irsa.alb_controller_role_arn }
output "irsa_external_dns_role_arn"      { value = module.iam_irsa.external_dns_role_arn }
output "irsa_cluster_autoscaler_role_arn"{ value = module.iam_irsa.cluster_autoscaler_role_arn }
output "irsa_app_s3_role_arn"            { value = module.iam_irsa.app_s3_role_arn }

# ECR/S3 outputs used by CI
output "ecr_repository_url" { value = module.ecr.repository_url }
output "data_bucket_name"   { value = module.s3.data_bucket_name }
output "artifacts_bucket_name" { value = module.s3.artifacts_bucket_name }

# Domain/alb logs (optional)
variable "alb_logs_bucket" { type = string, default = "" }
