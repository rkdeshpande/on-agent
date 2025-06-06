import logging
from pprint import pprint

from agents.offer_negotiation.agent import run_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    try:
        # Example usage with both deal_id and submission_id
        logger.info("Starting agent with submission ABC123...")
        result = run_agent(deal_id="TEST456", submission_id="ABC123")

        print("\n=== Final Result ===")
        pprint(result)

    except Exception as e:
        logger.error(f"Error running agent: {str(e)}")
        raise


if __name__ == "__main__":
    main()
