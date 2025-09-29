variable "alb_arn_suffix" { type = string } # e.g. app/abc123/def456
variable "cluster_name"   { type = string }

resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${var.cluster_name}-alb-5xx"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "HTTPCode_ELB_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Sum"
  threshold           = "5"
  dimensions = { LoadBalancer = var.alb_arn_suffix }
  alarm_description = "ALB 5xx spikes"
}

resource "aws_cloudwatch_metric_alarm" "eks_cpu_high" {
  alarm_name          = "${var.cluster_name}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 80
  metric_name         = "node_cpu_utilization"
  namespace           = "CWAgent"
  period              = 60
  statistic           = "Average"
  alarm_description   = "EKS node CPU > 80%"
}
