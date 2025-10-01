// Bicep template for MLOps Retail Forecast Infrastructure
// Alternative to Terraform for foundation layer deployment

param location string = resourceGroup().location
param environment string = 'dev'
param workspaceName string = 'amlws-retail-${environment}'
param storageName string = 'stretail${environment}'
param acrName string = 'acrretail${environment}'
param keyVaultName string = 'kv-retail-${environment}'
param appInsightsName string = 'appi-retail-${environment}'

// Storage Account with ADLS Gen2
resource storage 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    isHnsEnabled: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    deleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
  tags: {
    Project: 'MLOpsRetailForecast'
    Environment: environment
    Component: 'ml'
  }
}

// Storage Container
resource dataContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2022-09-01' = {
  parent: storage::blobServices
  name: 'data'
  properties: {
    publicAccess: 'None'
  }
}

// Key Vault with RBAC
resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enablePurgeProtection: true
    softDeleteRetentionInDays: 7
  }
  tags: {
    Project: 'MLOpsRetailForecast'
    Environment: environment
    Component: 'ml'
  }
}

// Container Registry
resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: acrName
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    adminUserEnabled: false
    policies: {
      trustPolicy: {
        enabled: true
      }
    }
  }
  tags: {
    Project: 'MLOpsRetailForecast'
    Environment: environment
    Component: 'ml'
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
  tags: {
    Project: 'MLOpsRetailForecast'
    Environment: environment
    Component: 'ml'
  }
}

// Azure ML Workspace
resource amlWorkspace 'Microsoft.MachineLearningServices/workspaces@2023-04-01' = {
  name: workspaceName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    description: 'Azure ML workspace for retail forecasting'
    friendlyName: 'RetailML-${environment}'
    storageAccount: storage.id
    containerRegistry: acr.id
    keyVault: keyVault.id
    applicationInsights: appInsights.id
  }
  tags: {
    Project: 'MLOpsRetailForecast'
    Environment: environment
    Component: 'ml'
  }
}

// AML Compute Cluster
resource computeCluster 'Microsoft.MachineLearningServices/workspaces/computes@2023-04-01' = {
  parent: amlWorkspace
  name: 'cpu-cluster'
  location: location
  properties: {
    computeType: 'AmlCompute'
    properties: {
      vmSize: 'Standard_DS3_v2'
      vmPriority: 'Dedicated'
      scaleSettings: {
        minNodeCount: 0
        maxNodeCount: 4
        nodeIdleTimeBeforeScaleDown: 'PT15M'
      }
    }
  }
}

// RBAC Assignments
resource acrPullAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(amlWorkspace.id, 'AcrPull')
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: amlWorkspace.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource storageReaderAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(amlWorkspace.id, 'StorageBlobDataReader')
  scope: storage
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1')
    principalId: amlWorkspace.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource kvSecretsAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(amlWorkspace.id, 'KeyVaultSecretsUser')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId: amlWorkspace.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Outputs
output workspaceId string = amlWorkspace.id
output workspaceName string = amlWorkspace.name
output storageAccountName string = storage.name
output acrName string = acr.name
output keyVaultName string = keyVault.name
output applicationInsightsName string = appInsights.name
