import logging
import os
import time
from pathlib import Path
from pprint import pformat

from dotenv import load_dotenv

from agents.offer_negotiation.agent import run_agent

# Load environment variables from secrets file
load_dotenv(Path("config/secrets.env"))
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is not set"


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
    """Display the results in a nice ASCII format."""
    # Print a few newlines to separate from previous output
    print("\n" * 2)

    # Header
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                    NEGOTIATION STRATEGY                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()

    # Deal Info
    print("📊 Deal Information")
    print("──────────────────")
    print(f"Deal ID: {result['deal_id']}")
    print(f"Submission ID: {result['submission_id']}")
    print()

    # Strategy
    print("🎯 Strategy")
    print("──────────")
    print(result.get("strategy", "No strategy generated"))
    print()

    # Talking Points
    print("💬 Key Talking Points")
    print("───────────────────")
    if result.get("talking_points"):
        for i, point in enumerate(result["talking_points"], 1):
            print(f"{i}. {point}")
    else:
        print("No talking points generated")
    print()

    # Rationale
    print("📝 Rationale")
    print("───────────")
    print(result.get("rationale_summary", "No rationale summary generated"))
    print()
    print("Detailed Analysis:")
    print("────────────────")
    print(result.get("detailed_rationale", "No detailed rationale generated"))
    print()

    # Performance Metrics
    print("⚡ Performance Metrics")
    print("───────────────────")
    if "node_timings" in result:
        start_time = result["node_timings"]["fetch_context"]["start"]
        end_time = result["node_timings"]["log_rationale"]["end"]
        print(f"Total execution time: {format_timing(start_time, end_time)}")
        print("\nPer-node timings:")
        for node, timing in result["node_timings"].items():
            print(f"- {node}: {format_timing(timing['start'], timing['end'])}")

    if "model_timings" in result:
        print("\nModel response times:")
        for call, timing in result["model_timings"].items():
            print(f"- {call}: {format_timing(timing['start'], timing['end'])}")

    print("\n" + "═" * 60)
    print()  # Final newline for spacing


def main():
    try:
        # Start overall timing
        overall_start = time.time()

        # Example usage with both deal_id and submission_id
        logger.info("Starting agent with submission ABC123...")

        # Run the agent and capture timing
        start_time = time.time()
        result = run_agent(deal_id="TEST456", submission_id="ABC123")
        end_time = time.time()

        # Debug logging to see what we got back
        logger.debug("Raw result from agent:")
        logger.debug(pformat(result))

        # Check if the strategy generation was successful
        if not result.get("ci_log_success", False):
            logger.error("Strategy generation failed. Check logs for details.")
            return

        # Display results in ASCII format
        display_results(result)

        # Log timing information
        logger.info("=== Performance Metrics ===")
        logger.info(
            f"Total execution time: {format_timing(overall_start, time.time())}"
        )
        logger.info(f"Agent execution time: {format_timing(start_time, end_time)}")

        # Log node timings if available
        if "node_timings" in result:
            logger.info("\nPer-node timings:")
            for node, timing in result["node_timings"].items():
                logger.info(
                    f"- {node}: {format_timing(timing['start'], timing['end'])}"
                )

        # Log model response times if available
        if "model_timings" in result:
            logger.info("\nModel response times:")
            for call, timing in result["model_timings"].items():
                logger.info(
                    f"- {call}: {format_timing(timing['start'], timing['end'])}"
                )

    except Exception as e:
        logger.error(f"Error running agent: {str(e)}")
        raise


if __name__ == "__main__":
    main()
