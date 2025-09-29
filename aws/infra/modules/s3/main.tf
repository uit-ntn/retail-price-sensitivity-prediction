variable "name_prefix" { type = string }
variable "kms_key_arn" { type = string }
variable "tags"        { type = map(string) }

locals { common = { bucket_key_enabled = true } }

resource "aws_s3_bucket" "data" {
  bucket = "${var.name_prefix}-data"
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    id     = "transition-cold"
    status = "Enabled"
    transition { days = 30, storage_class = "STANDARD_IA" }
    noncurrent_version_transition { noncurrent_days = 30, storage_class = "STANDARD_IA" }
    expiration { days = 365 }
  }
}

resource "aws_s3_bucket" "artifacts" {
  bucket = "${var.name_prefix}-artifacts"
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_arn
    }
    bucket_key_enabled = true
  }
}

output "data_bucket_name"      { value = aws_s3_bucket.data.bucket }
output "artifacts_bucket_name" { value = aws_s3_bucket.artifacts.bucket }
output "data_bucket_arn"       { value = aws_s3_bucket.data.arn }
