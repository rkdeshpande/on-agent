import logging

import yaml
from langchain_core.prompts import ChatPromptTemplate

from .utils import get_llm

# Configure logging
logger = logging.getLogger(__name__)

# Initialize model once at module level
model = get_llm()


def load_prompt_template():
    with open("config/prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)
    return prompts["negotiation_strategy"]


def generate_negotiation_strategy(state: dict) -> dict:
    """
    Generate a negotiation strategy based on the structured context.

    Args:
        state: The current state of the agent

    Returns:
        Dictionary containing the strategy and rationale
    """
    # Load and format the prompt
    prompt_template = load_prompt_template()
    prompt = ChatPromptTemplate.from_template(prompt_template)

    # Extract fields from structured_context
    context = state["structured_context"]

    formatted_prompt = prompt.format(
        broker_position=context["broker_position"],
        exposure_changes=context["exposure_changes"],
        price_arguments=context["price_arguments"],
        quote_constraints_MFP=context["quote_constraints_MFP"],
        quote_constraints_RTP=context["quote_constraints_RTP"],
        quote_constraints_WAP=context["quote_constraints_WAP"],
        negotiation_history=context["negotiation_history"],
        past_rationale=state["past_rationale"],
    )

    # Generate the response
    logger.info("Generating negotiation strategy...")
    try:
        response = model.invoke(formatted_prompt)
        logger.debug(f"Generated response: {response}")
    except Exception as e:
        logger.error(f"Error invoking model: {str(e)}")
        raise

    # Parse the response into the structured format
    try:
        # The response should be a JSON string, so we'll parse it
        import json

        result = json.loads(response.content)

        # Validate required fields
        required_fields = [
            "talking_points",
            "strategy",
            "rationale_summary",
            "detailed_rationale",
        ]
        missing_fields = [field for field in required_fields if field not in result]
        if missing_fields:
            error_msg = (
                f"Missing required fields in model response: "
                f"{', '.join(missing_fields)}"
            )
            logger.error(error_msg)
            logger.error(f"Raw response: {response.content}")
            raise ValueError(error_msg)

        return {**result, "ci_log_success": True}
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse model response as JSON: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Raw response: {response.content}")
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error processing model response: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Raw response: {response.content}")
        raise
