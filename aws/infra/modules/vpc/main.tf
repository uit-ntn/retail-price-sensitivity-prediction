variable "name_prefix"   { type = string }
variable "az_count"      { type = number }
variable "allowed_cidrs" { type = list(string) }
variable "tags"          { type = map(string) }

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.name_prefix}-vpc"
  cidr = "10.0.0.0/16"

  azs             = slice(data.aws_availability_zones.available.names, 0, var.az_count)
  private_subnets = ["10.0.1.0/24","10.0.2.0/24","10.0.11.0/24","10.0.12.0/24"][0:var.az_count]
  public_subnets  = ["10.0.101.0/24","10.0.102.0/24","10.0.111.0/24","10.0.112.0/24"][0:var.az_count]

  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true
  enable_dns_support   = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }

  tags = var.tags
}

data "aws_availability_zones" "available" {}

output "vpc_id"             { value = module.vpc.vpc_id }
output "private_subnet_ids" { value = module.vpc.private_subnets }
output "public_subnet_ids"  { value = module.vpc.public_subnets }
