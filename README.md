# Chat Web App for Azure AI Foundry Agent

A simple Flask web app with a chat window UI that calls an AI agent deployed to Azure AI Foundry. Designed for deployment to Azure App Service using `azd`.

## Project Structure

```
simpleApp/
├── azure.yaml              # azd project configuration
├── infra/                  # Bicep infrastructure templates
│   ├── main.bicep
│   ├── main.parameters.json
│   └── modules/
│       ├── appservice.bicep
│       ├── ai-role-assignment.bicep
│       └── monitoring.bicep
└── src/                    # Flask application
    ├── app.py
    ├── requirements.txt
    ├── templates/
    │   └── index.html
    └── static/
        ├── style.css
        └── script.js
```

## Prerequisites

- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- [Python 3.12+](https://www.python.org/downloads/)
- An Azure AI Foundry agent deployed and ready (you'll need the endpoint URL, agent name, and version)

## Run Locally

```bash
cd src
pip install -r requirements.txt
set AZURE_AI_FOUNDRY_ENDPOINT="https://your-account.services.ai.azure.com/api/projects/your-project"
set AZURE_AI_AGENT_NAME="your-agent-name"
set AZURE_AI_AGENT_VERSION="1"
python app.py
```

Open http://localhost:8000 in your browser.

## Configure Your Foundry Agent

Before deploying, set the environment variables for your Foundry agent:

```bash
azd env set AZURE_AI_FOUNDRY_ENDPOINT "https://your-account.services.ai.azure.com/api/projects/your-project"
azd env set AZURE_AI_AGENT_NAME "your-agent-name"
azd env set AZURE_AI_AGENT_VERSION "3"
```

To enable automatic role assignment (recommended), also set your AI account details:

```bash
azd env set AI_ACCOUNT_RESOURCE_GROUP "your-ai-account-resource-group"
azd env set AI_ACCOUNT_NAME "your-ai-account-name"
```

## Deploy to Azure

```bash
azd auth login
azd up
```

This will:
1. Provision an Azure App Service (Linux, Python 3.12) with Application Insights
2. Assign **Azure AI Developer** and **Cognitive Services User** roles to the App Service managed identity on your AI account (if `AI_ACCOUNT_RESOURCE_GROUP` and `AI_ACCOUNT_NAME` are set)
3. Deploy the Flask app
4. Output the URL of your deployed chat app

## Authentication

The app uses `DefaultAzureCredential` to authenticate with Foundry. The App Service is created with a **system-assigned managed identity**. Role assignments are handled automatically via Bicep when the `AI_ACCOUNT_RESOURCE_GROUP` and `AI_ACCOUNT_NAME` environment variables are configured.
