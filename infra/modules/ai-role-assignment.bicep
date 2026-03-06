targetScope = 'resourceGroup'

@description('Principal ID to assign the role to')
param principalId string

@description('Name of the AI Services account')
param aiAccountName string

// Role definition IDs
var azureAiDeveloperRoleId = '64702f94-c441-49e6-a78b-ef80e0188fee'
var cognitiveServicesUserRoleId = 'a97b65f3-24c7-4388-baec-2e87135dc908'

// Reference the existing AI Services account
resource aiAccount 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: aiAccountName
}

// Assign Azure AI Developer role (management plane)
resource aiDeveloperRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiAccount.id, principalId, azureAiDeveloperRoleId)
  scope: aiAccount
  properties: {
    principalId: principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', azureAiDeveloperRoleId)
    principalType: 'ServicePrincipal'
  }
}

// Assign Cognitive Services User role (data plane - required for agents/write)
resource cogServicesUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiAccount.id, principalId, cognitiveServicesUserRoleId)
  scope: aiAccount
  properties: {
    principalId: principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesUserRoleId)
    principalType: 'ServicePrincipal'
  }
}
