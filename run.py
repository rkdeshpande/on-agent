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

# Load environment variables from secrets file (if it exists)
load_dotenv(Path("config/secrets.env"), override=True)

# Load model settings
with open("config/model_settings.yaml", "r") as f:
    model_settings = yaml.safe_load(f)


# Configure logging
def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler
            logging.FileHandler(
                filename=log_dir / "agent.log",
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
    """Display the agent's results in a formatted way."""
    print("\n" + "═" * 60)
    print(" " * 20 + "NEGOTIATION STRATEGY" + " " * 20)
    print("═" * 60 + "\n")

    print("📊 Deal Information")
    print("──────────────────")
    print(f"Deal ID: {result['deal_id']}\n")

    print("🎯 Strategy")
    print("──────────")
    strategy = result.get("reasoning_output", {}).get("strategy", "")
    if strategy:
        print(strategy)
    else:
        print("No strategy generated")
    print()

    print("📝 Rationale")
    print("───────────")
    rationale = result.get("reasoning_output", {}).get("rationale", "")
    if rationale:
        print(rationale)
    else:
        print("No rationale generated")
    print()

    print("📚 Information Used")
    print("─────────────────")
    if "reasoning_output" in result:
        print("\nDeal Fields Used:")
        for field in result["reasoning_output"].get("used_deal_fields", []):
            print(f"- {field}")

        print("\nDomain Knowledge Used:")
        for chunk in result["reasoning_output"].get("used_domain_chunks", []):
            print(f"- {chunk['chunk_id']} ({chunk['type']}): {chunk['reason']}")
    print()

    print("🔄 Reasoning Steps")
    print("────────────────")
    for step in result.get("reasoning_steps", []):
        print(f"- {step}")
    print()

    print("═" * 60)
    print()  # Final newline for spacing


def main():
    try:
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
