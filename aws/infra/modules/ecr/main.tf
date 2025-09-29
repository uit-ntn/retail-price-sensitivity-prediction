variable "name_prefix"     { type = string }
variable "image_mutability"{ type = string, default = "IMMUTABLE" }
variable "scan_on_push"    { type = bool,   default = true }
variable "kms_key_arn"     { type = string, default = null }
variable "tags"            { type = map(string) }

resource "aws_ecr_repository" "server" {
  name                 = "${var.name_prefix}-server"
  image_tag_mutability = var.image_mutability
  image_scanning_configuration { scan_on_push = var.scan_on_push }
  encryption_configuration {
    encryption_type = var.kms_key_arn != null ? "KMS" : "AES256"
    kms_key        = var.kms_key_arn
  }
  tags = var.tags
}

output "repository_url" { value = aws_ecr_repository.server.repository_url }
