variable "name_prefix" { type = string }
variable "kms_key_arn" { type = string }
variable "tags"        { type = map(string) }

resource "aws_s3_bucket" "trail" {
  bucket = "${var.name_prefix}-cloudtrail"
  force_destroy = true
  tags = var.tags
}

resource "aws_s3_bucket_policy" "trail" {
  bucket = aws_s3_bucket.trail.id
  policy = data.aws_iam_policy_document.trail.json
}

data "aws_iam_policy_document" "trail" {
  statement {
    actions   = ["s3:GetBucketAcl"]
    resources = [aws_s3_bucket.trail.arn]
    principals { type = "Service", identifiers = ["cloudtrail.amazonaws.com"] }
  }
  statement {
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.trail.arn}/AWSLogs/*"]
    principals { type = "Service", identifiers = ["cloudtrail.amazonaws.com"] }
    condition { test = "StringEquals", variable = "s3:x-amz-acl", values = ["bucket-owner-full-control"] }
  }
}

resource "aws_cloudtrail" "this" {
  name                          = "${var.name_prefix}-trail"
  s3_bucket_name                = aws_s3_bucket.trail.id
  kms_key_id                    = var.kms_key_arn
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  include_global_service_events = true
  tags = var.tags
}
