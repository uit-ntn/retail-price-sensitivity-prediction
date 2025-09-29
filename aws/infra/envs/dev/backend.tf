terraform {
  backend "s3" {
    bucket = "REPLACE_ME-tfstate-dev"   # tạo trước bucket cho tfstate (bật versioning)
    key    = "aws-mlops/dev/terraform.tfstate"
    region = "ap-southeast-1"
    encrypt = true
    dynamodb_table = "REPLACE_ME-tflock-dev" # bảng DynamoDB để lock
  }
}
