variable "name_prefix"        { type = string }
variable "oidc_provider_arn"  { type = string }
variable "oidc_provider_url"  { type = string }
variable "s3_bucket_arn"      { type = string }
variable "tags"               { type = map(string) }

locals {
  sa_ns = "kube-system"
}

# Helper to build federated trust with EKS OIDC
data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals { type = "Federated", identifiers = [var.oidc_provider_arn] }
    condition {
      test     = "StringEquals"
      variable = "${replace(var.oidc_provider_url, "https://", "")}:sub"
      values = [
        "system:serviceaccount:${local.sa_ns}:aws-load-balancer-controller",
        "system:serviceaccount:${local.sa_ns}:external-dns",
        "system:serviceaccount:${local.sa_ns}:cluster-autoscaler"
      ]
    }
  }
}

# ALB controller permissions
data "aws_iam_policy_document" "alb" {
  statement { actions = ["elasticloadbalancing:*","iam:CreateServiceLinkedRole","ec2:Describe*","ec2:CreateTags","cognito-idp:DescribeUserPoolClient","acm:ListCertificates","acm:DescribeCertificate","waf-regional:GetWebACLForResource","waf-regional:GetWebACL","waf-regional:AssociateWebACL","waf-regional:DisassociateWebACL","wafv2:GetWebACLForResource","wafv2:GetWebACL","wafv2:AssociateWebACL","wafv2:DisassociateWebACL","shield:DescribeProtection","shield:GetSubscriptionState","shield:DeleteProtection","shield:CreateProtection","shield:DescribeSubscription","shield:ListProtections"], resources = ["*"] }
}

resource "aws_iam_role" "alb" {
  name               = "${var.name_prefix}-alb"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  tags               = var.tags
}
resource "aws_iam_policy" "alb" {
  name   = "${var.name_prefix}-alb"
  policy = data.aws_iam_policy_document.alb.json
}
resource "aws_iam_role_policy_attachment" "alb" {
  role       = aws_iam_role.alb.name
  policy_arn = aws_iam_policy.alb.arn
}

# external-dns (Route53)
data "aws_iam_policy_document" "external_dns" {
  statement {
    actions   = ["route53:ChangeResourceRecordSets"]
    resources = ["arn:aws:route53:::hostedzone/*"]
  }
  statement {
    actions   = ["route53:ListHostedZones","route53:ListResourceRecordSets"]
    resources = ["*"]
  }
}
resource "aws_iam_role" "external_dns" {
  name               = "${var.name_prefix}-external-dns"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  tags               = var.tags
}
resource "aws_iam_policy" "external_dns" {
  name   = "${var.name_prefix}-external-dns"
  policy = data.aws_iam_policy_document.external_dns.json
}
resource "aws_iam_role_policy_attachment" "external_dns" {
  role       = aws_iam_role.external_dns.name
  policy_arn = aws_iam_policy.external_dns.arn
}

# Cluster Autoscaler
data "aws_iam_policy_document" "cluster_autoscaler" {
  statement {
    actions = [
      "autoscaling:DescribeAutoScalingGroups",
      "autoscaling:DescribeAutoScalingInstances",
      "autoscaling:DescribeLaunchConfigurations",
      "autoscaling:DescribeTags",
      "autoscaling:SetDesiredCapacity",
      "autoscaling:TerminateInstanceInAutoScalingGroup",
      "ec2:DescribeLaunchTemplateVersions"
    ]
    resources = ["*"]
  }
}
resource "aws_iam_role" "cluster_autoscaler" {
  name               = "${var.name_prefix}-cluster-autoscaler"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  tags               = var.tags
}
resource "aws_iam_policy" "cluster_autoscaler" {
  name   = "${var.name_prefix}-cluster-autoscaler"
  policy = data.aws_iam_policy_document.cluster_autoscaler.json
}
resource "aws_iam_role_policy_attachment" "cluster_autoscaler" {
  role       = aws_iam_role.cluster_autoscaler.name
  policy_arn = aws_iam_policy.cluster_autoscaler.arn
}

# App access to S3 (read/write data bucket)
data "aws_iam_policy_document" "app_s3" {
  statement {
    actions   = ["s3:GetObject","s3:PutObject","s3:ListBucket"]
    resources = [var.s3_bucket_arn, "${var.s3_bucket_arn}/*"]
  }
}
resource "aws_iam_role" "app_s3" {
  name               = "${var.name_prefix}-app-s3"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  tags               = var.tags
}
resource "aws_iam_policy" "app_s3" {
  name   = "${var.name_prefix}-app-s3"
  policy = data.aws_iam_policy_document.app_s3.json
}
resource "aws_iam_role_policy_attachment" "app_s3" {
  role       = aws_iam_role.app_s3.name
  policy_arn = aws_iam_policy.app_s3.arn
}

output "alb_controller_role_arn"     { value = aws_iam_role.alb.arn }
output "external_dns_role_arn"       { value = aws_iam_role.external_dns.arn }
output "cluster_autoscaler_role_arn" { value = aws_iam_role.cluster_autoscaler.arn }
output "app_s3_role_arn"             { value = aws_iam_role.app_s3.arn }
