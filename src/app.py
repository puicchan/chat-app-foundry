import os
import logging
import sys
from flask import Flask, render_template, request, jsonify
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

app = Flask(__name__)

# Configure logging to stdout so App Service captures it
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Configure your Azure AI Foundry project endpoint and agent details
# Set these as environment variables or App Settings in Azure App Service
AZURE_AI_FOUNDRY_ENDPOINT = os.environ.get("AZURE_AI_FOUNDRY_ENDPOINT", "")
AZURE_AI_AGENT_NAME = os.environ.get("AZURE_AI_AGENT_NAME", "")
AZURE_AI_AGENT_VERSION = os.environ.get("AZURE_AI_AGENT_VERSION", "1")

# Cache the OpenAI client
_openai_client = None


def get_openai_client():
    """Create an OpenAI client from the AIProjectClient."""
    global _openai_client
    if _openai_client is None:
        project_client = AIProjectClient(
            endpoint=AZURE_AI_FOUNDRY_ENDPOINT,
            credential=DefaultAzureCredential(),
        )
        _openai_client = project_client.get_openai_client()
    return _openai_client


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Send a message to the Foundry Agent and return the response."""
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    if not AZURE_AI_FOUNDRY_ENDPOINT or not AZURE_AI_AGENT_NAME:
        return jsonify(
            {"error": "Agent not configured. Set AZURE_AI_FOUNDRY_ENDPOINT and AZURE_AI_AGENT_NAME."}
        ), 500

    try:
        logger.info(f"Chat request: '{user_message}', agent={AZURE_AI_AGENT_NAME}, version={AZURE_AI_AGENT_VERSION}")
        openai_client = get_openai_client()
        logger.info("Got OpenAI client, calling responses.create()...")

        # Call the agent using the OpenAI responses API with agent_reference
        response = openai_client.responses.create(
            input=[{"role": "user", "content": user_message}],
            extra_body={
                "agent_reference": {
                    "name": AZURE_AI_AGENT_NAME,
                    "version": AZURE_AI_AGENT_VERSION,
                    "type": "agent_reference",
                }
            },
        )

        logger.info(f"Got response, output_text length: {len(response.output_text) if response.output_text else 0}")
        return jsonify({"reply": response.output_text})

    except Exception as e:
        logger.error(f"Chat error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
