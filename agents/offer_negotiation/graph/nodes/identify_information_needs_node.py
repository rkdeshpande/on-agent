import logging
from typing import Callable

from langsmith import traceable

from agents.offer_negotiation.core.models.deal_models import DealContext
from agents.offer_negotiation.graph.state import DealContextState, InformationNeedsState

logger = logging.getLogger(__name__)


def create_identify_information_needs_node() -> Callable:
    """Create a node that identifies information needs from the deal context."""

    @traceable(name="identify_information_needs", run_type="chain")
    def identify_information_needs(state: DealContextState) -> InformationNeedsState:
        logger.info("=== Starting identify_information_needs node ===")
        logger.debug(f"Input state: {state}")

        # Extract deal context
        deal_context = DealContext(**state["deal_context"])

        # Identify information needs (example logic)
        information_needs = []
        if deal_context.submission.risk_profile:
            information_needs.append("submission.risk_profile")
        if deal_context.negotiation_context.objections:
            information_needs.append("negotiation_context.objections")

        logger.info(f"Identified information needs: {information_needs}")

        # Update state
        updated_state: InformationNeedsState = {
            **state,
            "information_needs": information_needs,
        }

        logger.info("=== Completed identify_information_needs node ===")
        logger.debug(f"Output state: {updated_state}")

        return updated_state

    return identify_information_needs
