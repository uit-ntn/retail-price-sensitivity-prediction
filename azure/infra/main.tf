# ---------- Resource Group ----------
resource "azurerm_resource_group" "rg" {
  name     = "${var.name_prefix}-rg"
  location = var.location
  tags     = var.tags
}

# ---------- Log Analytics & App Insights ----------
resource "azurerm_log_analytics_workspace" "law" {
  name                = "${var.name_prefix}-log"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

resource "azurerm_application_insights" "appi" {
  name                = "${var.name_prefix}-appi"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.law.id
  tags                = var.tags
}

# ---------- Storage (Blob/ADLS) ----------
resource "azurerm_storage_account" "st" {
  name                             = replace("${var.name_prefix}st", "-", "")
  resource_group_name              = azurerm_resource_group.rg.name
  location                         = var.location
  account_tier                     = "Standard"
  account_replication_type         = "LRS"
  min_tls_version                  = "TLS1_2"
  allow_nested_items_to_be_public  = false
  tags                             = var.tags
}

resource "azurerm_storage_container" "data" {
  name                  = "data"
  storage_account_name  = azurerm_storage_account.st.name
  container_access_type = "private"
}

# ---------- Key Vault (RBAC) ----------
data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "kv" {
  name                       = replace("${var.name_prefix}-kv", "_", "-")
  location                   = var.location
  resource_group_name        = azurerm_resource_group.rg.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  purge_protection_enabled   = true
  soft_delete_retention_days = 7
  enable_rbac_authorization  = true
  tags                       = var.tags
}

# ---------- Azure Container Registry ----------
resource "azurerm_container_registry" "acr" {
  name                = replace("${var.name_prefix}acr", "-", "")
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  sku                 = var.acr_sku
  admin_enabled       = false
  tags                = var.tags
}

# ---------- Azure ML Workspace ----------
resource "azurerm_machine_learning_workspace" "aml" {
  name                    = "${var.name_prefix}-amlws"
  location                = var.location
  resource_group_name     = azurerm_resource_group.rg.name

  application_insights_id = azurerm_application_insights.appi.id
  key_vault_id            = azurerm_key_vault.kv.id
  storage_account_id      = azurerm_storage_account.st.id
  container_registry_id   = azurerm_container_registry.acr.id

  identity { type = "SystemAssigned" }
  tags = var.tags
}

# ---------- AML Compute Cluster ----------
resource "azurerm_machine_learning_compute_cluster" "cpu" {
  name                          = "cpu-cluster"
  location                      = var.location
  machine_learning_workspace_id = azurerm_machine_learning_workspace.aml.id
  vm_size                       = "Standard_DS3_v2"

  scale_settings {
    min_node_count = 0
    max_node_count = 4
    scale_down_nodes_after_idle_duration = "PT15M"
  }
  tags = var.tags
}

# ---------- Cho AML kéo image từ ACR ----------
resource "azurerm_role_assignment" "acr_pull_to_aml" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_machine_learning_workspace.aml.identity[0].principal_id
}
