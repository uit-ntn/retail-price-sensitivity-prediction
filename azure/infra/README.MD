# Azure Infrastructure - Retail Forecast MLOps

Thư mục này chứa **Infrastructure as Code (IaC)** sử dụng **Terraform** và **Bicep** để triển khai toàn bộ hạ tầng Azure cho Retail Forecast MLOps pipeline.

---

## 📁 Cấu trúc thư mục

```
infra/
├── main.tf                   # Main Terraform configuration
├── variables.tf              # Variable definitions
├── output.tf                 # Output values
├── providers.tf              # Provider configurations
├── backend.tf                # Terraform state backend
├── alerts.tf                 # Application Insights alerts
├── online_endpoint.tf        # Azure ML online endpoint
├── main.bicep                # Bicep template (alternative)
├── dev.tfvars               # Development environment variables
├── prod.tfvars              # Production environment variables
├── parameters/              # Bicep parameter files
└── README.MD                # File này
```

---

## 🏗️ Terraform Configuration

### `main.tf` - Core Infrastructure
**Resources được tạo:**

#### 1. **Resource Group**
```hcl
resource "azurerm_resource_group" "rg" {
  name     = "${var.name_prefix}-rg"
  location = var.location
  tags     = var.tags
}
```

#### 2. **Log Analytics & Application Insights**
```hcl
resource "azurerm_log_analytics_workspace" "law" {
  name                = "${var.name_prefix}-log"
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_application_insights" "appi" {
  name                = "${var.name_prefix}-appi"
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.law.id
}
```

**Features:**
- Log Analytics workspace cho centralized logging
- Application Insights cho application monitoring
- 30-day log retention
- Web application type monitoring

#### 3. **Storage Account**
```hcl
resource "azurerm_storage_account" "st" {
  name                             = replace("${var.name_prefix}st", "-", "")
  account_tier                     = "Standard"
  account_replication_type         = "LRS"
  min_tls_version                  = "TLS1_2"
  allow_nested_items_to_be_public  = false
}

resource "azurerm_storage_container" "data" {
  name                  = "data"
  storage_account_name  = azurerm_storage_account.st.name
  container_access_type = "private"
}
```

**Security Features:**
- TLS 1.2 minimum
- Private blob access
- LRS replication
- No public nested items

#### 4. **Key Vault**
```hcl
resource "azurerm_key_vault" "kv" {
  name                       = replace("${var.name_prefix}-kv", "_", "-")
  sku_name                   = "standard"
  purge_protection_enabled   = true
  soft_delete_retention_days = 7
  enable_rbac_authorization  = true
}
```

**Security Features:**
- RBAC authorization enabled
- Purge protection
- 7-day soft delete retention
- Standard SKU

#### 5. **Azure Container Registry**
```hcl
resource "azurerm_container_registry" "acr" {
  name                = replace("${var.name_prefix}acr", "-", "")
  sku                 = var.acr_sku
  admin_enabled       = false
}
```

**Features:**
- Admin user disabled (security)
- Configurable SKU (Standard/Premium)
- Integrated với AML workspace

#### 6. **Azure ML Workspace**
```hcl
resource "azurerm_machine_learning_workspace" "aml" {
  name                    = "${var.name_prefix}-amlws"
  application_insights_id = azurerm_application_insights.appi.id
  key_vault_id            = azurerm_key_vault.kv.id
  storage_account_id      = azurerm_storage_account.st.id
  container_registry_id   = azurerm_container_registry.acr.id
  identity { type = "SystemAssigned" }
}
```

**Integrated Services:**
- Application Insights monitoring
- Key Vault for secrets
- Storage Account for artifacts
- Container Registry for images
- System-assigned managed identity

#### 7. **AML Compute Cluster**
```hcl
resource "azurerm_machine_learning_compute_cluster" "cpu" {
  name                          = "cpu-cluster"
  vm_size                       = "Standard_DS3_v2"
  
  scale_settings {
    min_node_count = 0
    max_node_count = 4
    scale_down_nodes_after_idle_duration = "PT15M"
  }
}
```

**Auto-scaling:**
- Scale to zero for cost optimization
- Maximum 4 nodes
- 15-minute idle timeout
- Standard_DS3_v2 instances

### `online_endpoint.tf` - ML Inference Endpoint
**Azure ML Online Endpoint** sử dụng AzAPI provider:

#### 1. **Online Endpoint**
```hcl
resource "azapi_resource" "online_endpoint" {
  type      = "Microsoft.MachineLearningServices/workspaces/onlineEndpoints@2023-10-01"
  name      = var.endpoint_name
  parent_id = azurerm_machine_learning_workspace.aml.id
  
  body = jsonencode({
    properties = { 
      authMode = "Key", 
      description = "Retail forecast endpoint" 
    }
  })
}
```

#### 2. **Blue Deployment**
```hcl
resource "azapi_resource" "online_deployment_blue" {
  type      = "Microsoft.MachineLearningServices/workspaces/onlineEndpoints/deployments@2023-10-01"
  name      = "blue"
  parent_id = azapi_resource.online_endpoint.id
  
  body = jsonencode({
    properties = {
      model = { name = var.model_name, version = var.model_version }
      environment = {
        image = "${azurerm_container_registry.acr.login_server}/retail/infer:${var.infer_image_tag}"
      }
      instanceType  = "Standard_DS3_v2"
      instanceCount = 1
      scaleSettings = { 
        scaleType = "Default", 
        minInstances = 1, 
        maxInstances = 3 
      }
    }
  })
}
```

**Configuration:**
- **Authentication:** Key-based
- **Instance:** Standard_DS3_v2
- **Scaling:** 1-3 instances
- **Health Checks:** /health endpoint
- **Timeout:** 60 seconds
- **Application Insights:** Enabled

#### 3. **Traffic Routing**
```hcl
resource "azapi_update_resource" "route_all_to_blue" {
  type        = "Microsoft.MachineLearningServices/workspaces/onlineEndpoints@2023-10-01"
  resource_id = azapi_resource.online_endpoint.id
  body = jsonencode({ 
    properties = { traffic = { blue = 100 } } 
  })
}
```

**Blue-Green Deployment:**
- 100% traffic to blue deployment
- Ready for green deployment
- Zero-downtime updates

### `alerts.tf` - Application Insights Alerts
**CloudWatch-style alerting** cho Azure:

```hcl
# Example alert configuration
resource "azurerm_monitor_metric_alert" "example" {
  name                = "retail-forecast-high-error-rate"
  resource_group_name = azurerm_resource_group.rg.name
  scopes              = [azurerm_application_insights.appi.id]
  description         = "High error rate alert"
  
  criteria {
    metric_namespace = "Microsoft.Insights/components"
    metric_name      = "exceptions/count"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 10
  }
}
```

---

## 🌍 Environment Management

### Development Environment (`dev.tfvars`)
```hcl
location     = "southeastasia"
name_prefix  = "retail-dev"
acr_sku      = "Standard"

endpoint_name   = "retail-forecast-endpoint"
model_name      = "retail-forecast"
model_version   = "1"
infer_image_tag = "latest"

tags = {
  Project     = "MLOpsRetailForecast"
  Environment = "dev"
  Component   = "ml"
  Owner       = "DataTeam"
  CostCenter  = "ML-Platform"
}

action_group_id = ""
```

### Production Environment (`prod.tfvars`)
```hcl
location     = "southeastasia"
name_prefix  = "retail-prod"
acr_sku      = "Premium"

endpoint_name   = "retail-forecast-prod-endpoint"
model_name      = "retail-forecast"
model_version   = "latest"
infer_image_tag = "stable"

tags = {
  Project     = "MLOpsRetailForecast"
  Environment = "production"
  Component   = "ml"
  Owner       = "DataTeam"
  CostCenter  = "ML-Platform"
}

action_group_id = "/subscriptions/.../actionGroups/prod-alerts"
```

**Differences:**
- **ACR SKU:** Standard vs Premium
- **Image Tags:** latest vs stable
- **Naming:** dev vs prod prefix
- **Alerting:** No alerts vs production alerts

---

## 🏗️ Bicep Alternative (`main.bicep`)

**Bicep template** cho native Azure deployment:

```bicep
param location string = resourceGroup().location
param workspaceName string = 'mlw-retail'
param storageName string = 'stmlretail'
param acrName string = 'acrmlretail'
param aksName string = 'aks-mlops-prod'

resource storage 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}

resource aml 'Microsoft.MachineLearningServices/workspaces@2023-04-01' = {
  name: workspaceName
  location: location
  properties: {
    description: 'Azure ML workspace for retail demand forecasting'
    friendlyName: 'RetailML'
    storageAccount: storage.id
    containerRegistry: acr.id
  }
}
```

**Usage:**
```bash
# Deploy với Bicep
az deployment group create \
  --resource-group rg-mlops \
  --template-file main.bicep \
  --parameters workspaceName=mlw-retail
```

---

## 🚀 Deployment Workflow

### 1. **Prerequisites**
```bash
# Install required tools
az extension add --name ml
terraform --version
az --version

# Login to Azure
az login
az account set --subscription "your-subscription-id"
```

### 2. **Terraform Backend Setup**
```bash
# Create storage account for Terraform state
az group create --name rg-terraform-state --location southeastasia

az storage account create \
  --name tfstateretailmlops \
  --resource-group rg-terraform-state \
  --location southeastasia \
  --sku Standard_LRS

# Create container
az storage container create \
  --name tfstate \
  --account-name tfstateretailmlops
```

### 3. **Infrastructure Deployment**
```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file="dev.tfvars"

# Apply configuration
terraform apply -var-file="dev.tfvars" -auto-approve

# Verify deployment
az ml workspace show --name retail-dev-amlws --resource-group retail-dev-rg
```

### 4. **Post-Deployment Setup**
```bash
# Configure Azure ML CLI
az configure --defaults group=retail-dev-rg workspace=retail-dev-amlws

# Test ACR access
az acr login --name retaildevacr

# Verify compute cluster
az ml compute list
```

---

## 🔧 Configuration Variables

### Required Variables (`variables.tf`):
```hcl
variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "southeastasia"
}

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
  validation {
    condition     = length(var.name_prefix) <= 10
    error_message = "Name prefix must be 10 characters or less."
  }
}

variable "acr_sku" {
  description = "Azure Container Registry SKU"
  type        = string
  default     = "Standard"
  validation {
    condition = contains(["Basic", "Standard", "Premium"], var.acr_sku)
    error_message = "ACR SKU must be Basic, Standard, or Premium."
  }
}

variable "endpoint_name" {
  description = "Azure ML online endpoint name"
  type        = string
}

variable "model_name" {
  description = "Model name for deployment"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
```

---

## 📊 Outputs (`output.tf`)

### Infrastructure Outputs:
```hcl
output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.rg.name
}

output "aml_workspace_name" {
  description = "Azure ML workspace name"
  value       = azurerm_machine_learning_workspace.aml.name
}

output "acr_login_server" {
  description = "ACR login server URL"
  value       = azurerm_container_registry.acr.login_server
}

output "storage_account_name" {
  description = "Storage account name"
  value       = azurerm_storage_account.st.name
}

output "application_insights_key" {
  description = "Application Insights instrumentation key"
  value       = azurerm_application_insights.appi.instrumentation_key
  sensitive   = true
}

output "online_endpoint_url" {
  description = "Azure ML online endpoint scoring URI"
  value       = azapi_resource.online_endpoint.output.properties.scoringUri
}
```

---

## 🔒 Security Best Practices

### 1. **Identity & Access Management**
```hcl
# System-assigned managed identity
identity { type = "SystemAssigned" }

# RBAC for ACR access
resource "azurerm_role_assignment" "acr_pull_to_aml" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_machine_learning_workspace.aml.identity[0].principal_id
}
```

### 2. **Network Security**
- Private storage containers
- Key Vault RBAC authorization
- TLS 1.2 minimum
- No admin users enabled

### 3. **Data Protection**
- Purge protection on Key Vault
- Soft delete retention
- Storage encryption at rest
- Private blob access

---

## 📈 Monitoring & Alerting

### Application Insights Integration:
```hcl
# Automatic integration với AML workspace
application_insights_id = azurerm_application_insights.appi.id

# Online endpoint monitoring
appInsightsEnabled = true
```

### Custom Alerts:
```bash
# Create action group for notifications
az monitor action-group create \
  --name "retail-alerts" \
  --resource-group retail-dev-rg \
  --action email "admin@company.com"

# Apply alerts configuration
terraform apply -var="action_group_id=/subscriptions/.../actionGroups/retail-alerts"
```

---

## 💰 Cost Optimization

### 1. **Compute Scaling**
```hcl
# Auto-scale to zero
min_node_count = 0
scale_down_nodes_after_idle_duration = "PT15M"

# Right-size instances
vm_size = "Standard_DS3_v2"  # 4 vCPU, 14 GB RAM
```

### 2. **Storage Optimization**
```hcl
# Local redundancy for dev
account_replication_type = "LRS"

# Log retention
retention_in_days = 30
```

### 3. **Registry Optimization**
```hcl
# Standard SKU for dev
acr_sku = "Standard"  # vs Premium for prod
```

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. **Terraform State Lock**
```bash
# Force unlock if stuck
terraform force-unlock LOCK_ID

# Check state
terraform state list
```

#### 2. **AzAPI Provider Issues**
```bash
# Update AzAPI provider
terraform init -upgrade

# Check provider version
terraform providers
```

#### 3. **ACR Access Issues**
```bash
# Check role assignment
az role assignment list --scope /subscriptions/.../resourceGroups/.../providers/Microsoft.ContainerRegistry/registries/...

# Test ACR login
az acr login --name retaildevacr
```

#### 4. **Online Endpoint Deployment Failures**
```bash
# Check endpoint status
az ml online-endpoint show --name retail-forecast-endpoint

# Check deployment logs
az ml online-deployment get-logs --name blue --endpoint retail-forecast-endpoint
```

---

## 📚 Tài liệu tham khảo

- [Azure Machine Learning Terraform Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/machine_learning_workspace)
- [AzAPI Terraform Provider](https://registry.terraform.io/providers/Azure/azapi/latest/docs)
- [Azure ML Online Endpoints](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-deploy-online-endpoints)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Bicep Documentation](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
