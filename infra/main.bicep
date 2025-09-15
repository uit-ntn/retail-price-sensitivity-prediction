param location string = resourceGroup().location
param workspaceName string = 'mlw-retail'
param storageName string = 'stmlretail'
param acrName string = 'acrmlretail'
param aksName string = 'aks-mlops-prod'

resource storage 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

resource acr 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
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

resource aks 'Microsoft.ContainerService/managedClusters@2023-07-01' = {
  name: aksName
  location: location
  sku: {
    name: 'Basic'
    tier: 'Free'
  }
  properties: {
    dnsPrefix: 'retailaks'
    agentPoolProfiles: [
      {
        name: 'nodepool1'
        count: 3
        vmSize: 'Standard_DS3_v2'
        osType: 'Linux'
        mode: 'System'
      }
    ]
    identity: {
      type: 'SystemAssigned'
    }
  }
}
