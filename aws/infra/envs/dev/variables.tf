variable "project"        { type = string  default = "retail-forecast" }
variable "env"            { type = string  default = "dev" }
variable "region"         { type = string  default = "ap-southeast-1" }
variable "az_count"       { type = number  default = 2 }
variable "cluster_version"{ type = string  default = "1.30" }
variable "instance_types" { type = list(string) default = ["m6i.large","m5.large"] }
variable "spot"           { type = bool    default = true }
variable "allowed_cidrs"  { type = list(string) default = ["0.0.0.0/0"] } # demo
variable "domain_name"    { type = string  default = "dev.REPLACE_ME.example.com" }
variable "alb_logs_bucket"{ type = string  default = "" } # optional
