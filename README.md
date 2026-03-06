# Chat Web App for Azure AI Foundry Agent

A simple Flask web app with a chat window UI that calls an AI agent deployed to Azure AI Foundry. Designed for deployment to Azure App Service using `azd`.

## Project Structure

```
simpleApp/
├── azure.yaml              # azd project configuration
├── infra/                  # Bicep infrastructure templates
│   ├── main.bicep
│   ├── main.parameters.bicepparam
│   └── modules/
│       ├── appservice.bicep
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
- An Azure AI Foundry agent deployed and ready (you'll need the endpoint URL and agent ID)

## Run Locally

```bash
cd src
pip install -r requirements.txt
python app.py
```

Open http://localhost:8000 in your browser.

## Configure Your Foundry Agent

Before deploying, set the environment variables for your Foundry agent:

```bash
azd env set AZURE_AI_FOUNDRY_ENDPOINT "https://your-project.services.ai.azure.com"
azd env set AZURE_AI_AGENT_ID "your-agent-id"
```

## Deploy to Azure

```bash
azd auth login
azd up
```

This will:
1. Provision an Azure App Service (Linux, Python 3.12) with Application Insights
2. Deploy the Flask app
3. Output the URL of your deployed chat app

## Authentication

The app uses `DefaultAzureCredential` to authenticate with Foundry. The App Service is created with a **system-assigned managed identity**. After deployment, grant this identity the required role on your AI Foundry project:

```bash
# Get the principal ID from azd outputs, then assign role
az role assignment create \
  --assignee <principal-id> \
  --role "Azure AI Developer" \
  --scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.MachineLearningServices/workspaces/<project>
```
