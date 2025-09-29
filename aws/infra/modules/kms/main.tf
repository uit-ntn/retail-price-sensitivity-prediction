variable "name_prefix" { type = string }
variable "tags"        { type = map(string) }

resource "aws_kms_key" "this" {
  description         = "${var.name_prefix} cmk"
  deletion_window_in_days = 7
  enable_key_rotation = true
  tags                = var.tags
}

resource "aws_kms_alias" "this" {
  name          = "alias/${var.name_prefix}-cmk"
  target_key_id = aws_kms_key.this.key_id
}

output "kms_key_arn" { value = aws_kms_key.this.arn }
