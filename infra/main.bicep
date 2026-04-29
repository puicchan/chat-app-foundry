targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment (used for resource naming)')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Tags to apply to all resources')
param tags object = {}

// Optional: Azure AI Project endpoint and agent ID (set via azd env set)
@description('Azure AI Project endpoint URL')
param azureAiProjectEndpoint string = ''

@description('Azure AI Foundry Agent name')
param azureAiAgentName string = ''

@description('Azure AI Foundry Agent version')
param azureAiAgentVersion string = '1'

@description('Resource group containing the AI Services account')
param aiAccountResourceGroup string = ''

@description('Name of the AI Services account')
param aiAccountName string = ''

// Generate a unique suffix for resource names
var resourceSuffix = take(uniqueString(subscription().id, environmentName, location), 6)
var resourceGroupName = 'rg-${environmentName}'
var allTags = union(tags, {
  'azd-env-name': environmentName
})

// Create the resource group
resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: allTags
}

// Log Analytics Workspace for monitoring
module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  scope: rg
  params: {
    name: 'log-${environmentName}-${resourceSuffix}'
    location: location
    tags: allTags
  }
}

// App Service (Linux + Python)
module appService 'modules/appservice.bicep' = {
  name: 'appservice'
  scope: rg
  params: {
    name: 'app-${environmentName}-${resourceSuffix}'
    planName: 'plan-${environmentName}-${resourceSuffix}'
    location: location
    tags: union(allTags, {
      'azd-service-name': 'web'
    })
    appInsightsConnectionString: monitoring.outputs.appInsightsConnectionString
    azureAiProjectEndpoint: azureAiProjectEndpoint
    azureAiAgentName: azureAiAgentName
    azureAiAgentVersion: azureAiAgentVersion
  }
}

// Role assignment: grant App Service identity "Azure AI Developer" on the AI account
module aiRoleAssignment 'modules/ai-role-assignment.bicep' = if (!empty(aiAccountResourceGroup) && !empty(aiAccountName)) {
  name: 'ai-role-assignment'
  scope: resourceGroup(aiAccountResourceGroup)
  params: {
    principalId: appService.outputs.principalId
    aiAccountName: aiAccountName
  }
}

output AZURE_LOCATION string = location
output SERVICE_WEB_URL string = appService.outputs.url
output SERVICE_WEB_NAME string = appService.outputs.name
output RESOURCE_GROUP_NAME string = rg.name
