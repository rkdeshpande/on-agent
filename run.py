import logging
import os
import time
from datetime import datetime
from pathlib import Path
from pprint import pformat
from typing import Dict

import yaml
from dotenv import load_dotenv

from agents.offer_negotiation.agent import run_agent
from config.app_config import config

# Load environment variables from secrets file (if it exists)
load_dotenv(config.secrets_env_path, override=True)

# Load model settings
with open(config.model_settings_path, "r") as f:
    model_settings = yaml.safe_load(f)


# Configure logging
def setup_logging():
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler
            logging.FileHandler(
                filename=config.log_file_path,
                mode="a",  # append mode
                encoding="utf-8",
            ),
        ],
    )

    # Set specific loggers to INFO
    loggers = [
        "agents.offer_negotiation.agent",
        "agents.offer_negotiation.communication",
        "agents.offer_negotiation.reasoning",
        "agents.offer_negotiation.memory",
        "agents.offer_negotiation.utils",
    ]
    for logger_name in loggers:
        logging.getLogger(logger_name).setLevel(logging.INFO)


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def format_timing(start_time: float, end_time: float) -> str:
    """Format timing information in a readable way."""
    duration = end_time - start_time
    return f"{duration:.2f}s"


def display_results(result: dict):
    """Display the agent's results in a robust, future-proof way."""
    print("\n" + "═" * 60)
    print(" " * 20 + "NEGOTIATION AGENT OUTPUT" + " " * 20)
    print("═" * 60 + "\n")

    # Deal ID
    deal_id = result.get("deal_id")
    if deal_id:
        print(f"📊 Deal ID: {deal_id}\n")

    # Decision Basis
    if "decision_basis" in result and result["decision_basis"]:
        print("🎯 Decision Rules Applied\n──────────────────────")
        for decision in result["decision_basis"]:
            print(f"- {decision['heuristic']}")
            print(f"  Justification: {decision['justification']}")
            print(f"  Confidence: {decision['confidence']}\n")

    # Reasoning Steps
    if "reasoning_steps" in result:
        print("🔄 Reasoning Steps\n────────────────")
        for step in result["reasoning_steps"]:
            print(f"- {step}")
        print()

    # Information Needs
    if "information_needs" in result:
        print("📚 Information Needs\n────────────────────")
        for need in result["information_needs"]:
            print(f"- {need}")
        print()

    # Domain Knowledge Used
    if "domain_chunks" in result and result["domain_chunks"]:
        print("📖 Domain Knowledge Used\n───────────────────────")
        for chunk in result["domain_chunks"]:
            chunk_id = chunk.get("chunk_id", "Unknown")
            content = chunk.get("content", "")
            doc_type = chunk.get("metadata", {}).get("document_type", "Unknown")
            print(f"- {chunk_id} [{doc_type}]: {content[:100]}...")
        print()

    print("═" * 60)
    print()  # Final newline for spacing


def main():
    try:
        # Validate configuration
        if not config.validate():
            logger.error(
                "Configuration validation failed. Please check the errors above."
            )
            return

        # Example usage
        logger.info("Starting agent with deal DEAL123...")

        # Run the agent
        result = run_agent(deal_id="DEAL123", model_settings=model_settings)

        # Debug logging to see what we got back
        logger.debug("Raw result from agent:")
        logger.debug(pformat(result))

        # Display results in ASCII format
        display_results(result)

    except Exception as e:
        logger.error(f"Error running agent: {str(e)}")
        raise


if __name__ == "__main__":
    main()
