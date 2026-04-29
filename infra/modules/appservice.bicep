targetScope = 'resourceGroup'

@description('Name of the App Service')
param name string

@description('Name of the App Service Plan')
param planName string

@description('Location for all resources')
param location string = resourceGroup().location

@description('Tags to apply to all resources')
param tags object = {}

@description('Application Insights connection string')
param appInsightsConnectionString string = ''

@description('Azure AI Project endpoint URL')
param azureAiProjectEndpoint string = ''

@description('Azure AI Foundry Agent name')
param azureAiAgentName string = ''

@description('Azure AI Foundry Agent version')
param azureAiAgentVersion string = '1'

// App Service Plan (Linux, B1 SKU)
resource appServicePlan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: planName
  location: location
  tags: tags
  kind: 'linux'
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  properties: {
    reserved: true // Required for Linux
  }
}

// App Service
resource appService 'Microsoft.Web/sites@2024-04-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12'
      appCommandLine: 'gunicorn --bind=0.0.0.0 --timeout 600 app:app'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      appSettings: [
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsightsConnectionString
        }
        {
          name: 'AZURE_AI_PROJECT_ENDPOINT'
          value: azureAiProjectEndpoint
        }
        {
          name: 'AZURE_AI_AGENT_NAME'
          value: azureAiAgentName
        }
        {
          name: 'AZURE_AI_AGENT_VERSION'
          value: azureAiAgentVersion
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
      ]
    }
  }
}

output url string = 'https://${appService.properties.defaultHostName}'
output name string = appService.name
output principalId string = appService.identity.principalId
