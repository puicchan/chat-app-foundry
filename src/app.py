import os
import logging
import sys
import uuid
from flask import Flask, render_template, request, jsonify
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import VersionRefIndicator
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
AZURE_AI_PROJECT_ENDPOINT = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
AZURE_AI_AGENT_NAME = os.environ.get("AZURE_AI_AGENT_NAME", "")

# Cache the project client
_project_client = None


def get_project_client():
    """Create and cache an AIProjectClient."""
    global _project_client
    if _project_client is None:
        _project_client = AIProjectClient(
            endpoint=AZURE_AI_PROJECT_ENDPOINT,
            credential=DefaultAzureCredential(),
            allow_preview=True,
        )
    return _project_client


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

    if not AZURE_AI_PROJECT_ENDPOINT or not AZURE_AI_AGENT_NAME:
        return jsonify(
            {"error": "Agent not configured. Set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_AGENT_NAME."}
        ), 500

    try:
        logger.info(f"Chat request: '{user_message}', agent={AZURE_AI_AGENT_NAME}")
        project_client = get_project_client()

        # Get the agent to find the latest version
        agent = project_client.agents.get(agent_name=AZURE_AI_AGENT_NAME)
        latest_version = agent.versions["latest"].version
        logger.info(f"Agent: {agent.name}, version: {latest_version}")

        isolation_key = str(uuid.uuid4())

        # Create a session for conversation state
        session = project_client.beta.agents.create_session(
            agent_name=AZURE_AI_AGENT_NAME,
            isolation_key=isolation_key,
            version_indicator=VersionRefIndicator(agent_version=latest_version),
        )
        logger.info(f"Created session: {session.agent_session_id}")

        try:
            # Create an OpenAI client bound to the agent endpoint
            openai_client = project_client.get_openai_client(agent_name=AZURE_AI_AGENT_NAME)

            # Call Responses API with the session
            response = openai_client.responses.create(
                input=user_message,
                extra_body={
                    "agent_session_id": session.agent_session_id,
                },
            )
            logger.info(f"Got response, output_text length: {len(response.output_text) if response.output_text else 0}")
            return jsonify({"reply": response.output_text})

        finally:
            # Clean up the session
            project_client.beta.agents.delete_session(
                agent_name=AZURE_AI_AGENT_NAME,
                session_id=session.agent_session_id,
                isolation_key=isolation_key,
            )
            logger.info(f"Deleted session: {session.agent_session_id}")

    except Exception as e:
        logger.error(f"Chat error: {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
