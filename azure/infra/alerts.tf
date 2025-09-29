resource "azurerm_monitor_metric_alert" "ai_p95_latency" {
  name                = "${var.name_prefix}-ai-p95-latency-high"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_application_insights.appi.id]
  description         = "P95 request duration high"
  severity            = 2
  frequency           = "PT1M"
  window_size         = "PT5M"
  auto_mitigate       = true
  enabled             = true

  criteria {
    metric_namespace = "microsoft.insights/components"
    metric_name      = "requests/duration"
    aggregation      = "Percentile95"
    operator         = "GreaterThan"
    threshold        = 400
  }

  dynamic "action" {
    for_each = var.action_group_id == "" ? [] : [1]
    content { action_group_id = var.action_group_id }
  }

  tags = var.tags
}
