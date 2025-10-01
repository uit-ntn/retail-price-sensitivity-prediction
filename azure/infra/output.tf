output "resource_group"   { value = azurerm_resource_group.rg.name }
output "workspace_name"   { value = azurerm_machine_learning_workspace.aml.name }
output "acr_login_server" { value = azurerm_container_registry.acr.login_server }
output "storage_account_name" { value = azurerm_storage_account.st.name }
output "key_vault_name" { value = azurerm_key_vault.kv.name }
output "application_insights_name" { value = azurerm_application_insights.appi.name }
# output "endpoint_name"    { value = azapi_resource.online_endpoint.name }
# output "endpoint_id"      { value = azapi_resource.online_endpoint.id }
