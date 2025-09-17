output "s3_data_bucket" {
  value = aws_s3_bucket.data.bucket
}

output "s3_artifacts_bucket" {
  value = aws_s3_bucket.artifacts.bucket
}
