import logging
from typing import Callable, List

from langsmith import traceable

from agents.offer_negotiation.core.models.deal_models import DealContext
from agents.offer_negotiation.graph.state import DealContextState, InformationNeedsState

logger = logging.getLogger(__name__)


def analyze_objections(objections: List[str]) -> List[str]:
    """Analyze objections to identify specific information needs."""
    needs = []

    for objection in objections:
        objection_lower = objection.lower()

        # Premium-related objections
        if any(term in objection_lower for term in ["premium", "price", "cost"]):
            needs.append("negotiation_context.premium_objections")

        # Deductible-related objections
        if "deductible" in objection_lower:
            needs.append("negotiation_context.deductible_objections")

        # Coverage-related objections
        if any(term in objection_lower for term in ["coverage", "limit", "exclusion"]):
            needs.append("negotiation_context.coverage_objections")
            needs.append("submission.coverage_terms")

        # Risk-related objections
        if any(term in objection_lower for term in ["risk", "hazard", "exposure"]):
            needs.append("submission.risk_profile")

    return needs


def create_identify_information_needs_node() -> Callable:
    """Create a node that identifies information needs from the deal context."""

    @traceable(name="identify_information_needs", run_type="chain")
    def identify_information_needs(state: DealContextState) -> InformationNeedsState:
        logger.info("=== Starting identify_information_needs node ===")
        logger.debug(f"Input state: {state}")

        # Extract deal context
        deal_context = DealContext(**state["deal_context"])

        # Start with basic needs
        information_needs = ["submission.risk_profile"]  # Always need risk profile

        # Add needs based on objections
        if deal_context.negotiation_context.objections:
            objection_needs = analyze_objections(
                deal_context.negotiation_context.objections
            )
            information_needs.extend(
                needs for needs in objection_needs if needs not in information_needs
            )

        # Add needs based on coverage terms
        if deal_context.submission.coverage_terms:
            information_needs.append("submission.coverage_terms")

        # Add needs based on client history
        if deal_context.client_history.prior_negotiations:
            information_needs.append("client_history.prior_negotiations")

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
