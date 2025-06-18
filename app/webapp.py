from flask import Flask, request, jsonify, render_template, abort, send_from_directory
import yaml
import json
from dotenv import load_dotenv
from agents.offer_negotiation.agent import run_agent
from config.app_config import config

# Load environment variables from secrets file (if it exists)
load_dotenv(config.secrets_env_path, override=True)

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')

# Load model settings
with open(config.model_settings_path, "r") as f:
    model_settings = yaml.safe_load(f)


def make_json_serializable(obj):
    """Convert an object to JSON serializable format."""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif hasattr(obj, 'model_dump'):  # Pydantic models
        return obj.model_dump()
    elif hasattr(obj, '__dict__'):  # Custom objects
        return str(obj)
    else:
        try:
            json.dumps(obj)  # Test if it's already serializable
            return obj
        except (TypeError, ValueError):
            return str(obj)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)


@app.route("/run", methods=["POST"])
def run_agent_endpoint():
    deal_id = request.form.get("deal_id")

    if not deal_id:
        abort(400, description="deal_id is required")

    try:
        result = run_agent(deal_id=deal_id, model_settings=model_settings)
        
        # Convert to JSON serializable format
        serializable_result = make_json_serializable(result)
        
        return jsonify({"success": True, "result": serializable_result})
    except Exception as e:
        abort(500, description=str(e))


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": error.description}), 400


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": error.description}), 500
