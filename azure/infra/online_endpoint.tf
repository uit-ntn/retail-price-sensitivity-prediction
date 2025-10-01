# OPTIONAL: Managed Online Endpoint + Deployment 'blue' qua AzAPI
# Uncomment và configure variables nếu muốn deploy endpoint trong Task 7
# Thông thường endpoint sẽ được tạo ở Task 12-13

# resource "azapi_resource" "online_endpoint" {
#   type      = "Microsoft.MachineLearningServices/workspaces/onlineEndpoints@2023-10-01"
#   name      = var.endpoint_name
#   parent_id = azurerm_machine_learning_workspace.aml.id
#   location  = var.location
#   identity  { type = "SystemAssigned" }
# 
#   body = jsonencode({
#     properties = { authMode = "Key", description = "Retail forecast endpoint" }
#     tags       = var.tags
#   })
# }

# resource "azapi_resource" "online_deployment_blue" {
#   type      = "Microsoft.MachineLearningServices/workspaces/onlineEndpoints/deployments@2023-10-01"
#   name      = "blue"
#   parent_id = azapi_resource.online_endpoint.id
#   location  = var.location
# 
#   body = jsonencode({
#     properties = {
#       model = { name = var.model_name, version = var.model_version }
#       environment = {
#         image = "${azurerm_container_registry.acr.login_server}/retail/infer:${var.infer_image_tag}"
#       }
#       instanceType  = "Standard_DS3_v2"
#       instanceCount = 1
#       livenessProbe  = { path = "/health", port = 8080 }
#       readinessProbe = { path = "/health", port = 8080 }
#       requestSettings = {
#         requestTimeoutMs                 = 60000
#         maxConcurrentRequestsPerInstance = 1
#         maxQueueWaitMs                   = 60000
#       }
#       scaleSettings = { scaleType = "Default", minInstances = 1, maxInstances = 3 }
#       appInsightsEnabled = true
#     }
#     tags = var.tags
#   })
# 
#   depends_on = [azapi_resource.online_endpoint]
# }
# 
# resource "azapi_update_resource" "route_all_to_blue" {
#   type        = "Microsoft.MachineLearningServices/workspaces/onlineEndpoints@2023-10-01"
#   resource_id = azapi_resource.online_endpoint.id
#   body = jsonencode({ properties = { traffic = { blue = 100 } } })
#   depends_on = [azapi_resource.online_deployment_blue]
# }
