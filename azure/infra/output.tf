output "resource_group"   { value = azurerm_resource_group.rg.name }
output "workspace_name"   { value = azurerm_machine_learning_workspace.aml.name }
output "acr_login_server" { value = azurerm_container_registry.acr.login_server }
output "endpoint_name"    { value = azapi_resource.online_endpoint.name }
output "endpoint_id"      { value = azapi_resource.online_endpoint.id }
