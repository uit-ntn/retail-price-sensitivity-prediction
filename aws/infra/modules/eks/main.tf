variable "name_prefix"       { type = string }
variable "cluster_version"   { type = string }
variable "vpc_id"            { type = string }
variable "private_subnet_ids"{ type = list(string) }
variable "public_subnet_ids" { type = list(string) }
variable "instance_types"    { type = list(string) }
variable "spot"              { type = bool }
variable "tags"              { type = map(string) }

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.8"

  cluster_name    = "${var.name_prefix}-eks"
  cluster_version = var.cluster_version

  vpc_id                   = var.vpc_id
  subnet_ids               = var.private_subnet_ids
  control_plane_subnet_ids = var.private_subnet_ids

  enable_irsa = true

  eks_managed_node_groups = {
    default = {
      instance_types = var.instance_types
      ami_type       = "AL2_x86_64"
      capacity_type  = var.spot ? "SPOT" : "ON_DEMAND"
      min_size = 1
      max_size = 5
      desired_size = 2
      labels = { "workload" = "general" }
    }
  }

  tags = var.tags
}

output "cluster_name"        { value = module.eks.cluster_name }
output "oidc_provider_arn"   { value = module.eks.oidc_provider_arn }
output "oidc_provider_url"   { value = module.eks.oidc_provider }
