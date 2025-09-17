provider "aws" {
  region = "ap-southeast-1"
}

resource "aws_s3_bucket" "data" {
  bucket = "retail-mlops-data-${var.account_id}-${var.region}"
  force_destroy = true
}

resource "aws_s3_bucket" "artifacts" {
  bucket = "retail-mlops-artifacts-${var.account_id}-${var.region}"
  force_destroy = true
}

resource "aws_iam_role" "sagemaker_exec_role" {
  name = "sagemaker-exec-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "sagemaker.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "sagemaker_full" {
  role       = aws_iam_role.sagemaker_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

output "sagemaker_exec_role_arn" {
  value = aws_iam_role.sagemaker_exec_role.arn
}
