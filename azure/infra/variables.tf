variable "location"     { type = string  default = "southeastasia" }
variable "name_prefix"  { type = string  default = "retail-dev" }
variable "acr_sku"      { type = string  default = "Standard" }

variable "tags" {
  type = map(string)
  default = {
    Project     = "MLOpsRetailForecast"
    Environment = "dev"
    Component   = "ml"
    Owner       = "DataTeam"
    CostCenter  = "ML-Platform"
  }
}

# Online endpoint/deployment
variable "endpoint_name"   { type = string default = "retail-forecast-endpoint" }
variable "model_name"      { type = string default = "retail-forecast" }
variable "model_version"   { type = string default = "1" }
variable "infer_image_tag" { type = string default = "latest" }

# Alert (optional)
variable "action_group_id" {
  type        = string
  default     = ""
  description = "Resource ID của Action Group; để rỗng nếu chưa có"
}
