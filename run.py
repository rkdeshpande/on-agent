import logging
import os
from pathlib import Path
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

        # Log successful completion
        logger.info("Agent execution completed successfully")
        logger.info(f"Deal ID: {result.get('deal_id', 'Unknown')}")
        logger.info(f"Strategy: {result.get('strategy', 'NOT FOUND')}")
        logger.info(f"Rationale: {result.get('rationale', 'NOT FOUND')}")

    except Exception as e:
        logger.error(f"Error running agent: {str(e)}")
        raise


if __name__ == "__main__":
    main()
