import yaml
from flask import Flask, abort, jsonify, render_template, request

from agents.offer_negotiation.agent import run_agent
from config.app_config import config

app = Flask(__name__)

# Load model settings
with open(config.model_settings_path, "r") as f:
    model_settings = yaml.safe_load(f)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run_agent_endpoint():
    deal_id = request.form.get("deal_id")

    if not deal_id:
        abort(400, description="deal_id is required")

    try:
        result = run_agent(deal_id=deal_id, model_settings=model_settings)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        abort(500, description=str(e))


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": error.description}), 400


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": error.description}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
