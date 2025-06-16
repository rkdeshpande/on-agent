import json
import logging
from datetime import UTC, datetime
from typing import Callable, List

from langsmith import traceable

from agents.offer_negotiation.core.models.deal_models import DealContext
from agents.offer_negotiation.graph.interfaces import (
    IDENTIFY_INFORMATION_NEEDS_METADATA,
)
from agents.offer_negotiation.graph.state import DealContextState, InformationNeedsState
from agents.offer_negotiation.graph.utils import log_state
from agents.offer_negotiation.utils.trace_metadata import (
    add_error_metadata,
    add_performance_metadata,
    create_trace_metadata,
)

logger = logging.getLogger(__name__)


def analyze_objections(objections: List[str]) -> List[str]:
    """Analyze objections to identify required information."""
    needs = []
    for objection in objections:
        objection = objection.lower()
        if "premium" in objection:
            needs.append("submission.premium_structure")
        if "coverage" in objection:
            needs.append("submission.coverage_terms")
        if "deductible" in objection:
            needs.append("submission.deductible")
    return needs


def create_identify_information_needs_node() -> Callable:
    """Create a node that identifies information needs from the deal context."""

    @traceable(
        name=IDENTIFY_INFORMATION_NEEDS_METADATA.name,
        run_type="chain",
        metadata=IDENTIFY_INFORMATION_NEEDS_METADATA.model_dump(),
    )
    def identify_information_needs(state: DealContextState) -> InformationNeedsState:
        """Identify information needs for the negotiation strategy."""
        # Create trace metadata
        start_time = datetime.now(UTC)
        trace = create_trace_metadata("identify_information_needs", state)

        try:
            logger.info("=== Starting identify_information_needs node ===")
            log_state(state, "Input ")

            # Validate required fields
            if not state.deal_context:
                raise ValueError("deal_context is required")

            # Log input state
            logger.info(f"Input state: {json.dumps(state.model_dump(), indent=2)}")

            # Identify information needs based on deal context
            information_needs = []
            deal_context = state.deal_context
            if "submission" in deal_context:
                submission = deal_context["submission"]
                if "risk_profile" in submission:
                    information_needs.append("submission.risk_profile")
                if "premium_structure" in submission:
                    information_needs.append("submission.premium_structure")
                if "deductible" in submission:
                    information_needs.append("submission.deductible")
                if "coverage_terms" in submission:
                    information_needs.append("submission.coverage_terms")
            if "client_history" in deal_context:
                client_history = deal_context["client_history"]
                if "prior_negotiations" in client_history:
                    information_needs.append("client_history.prior_negotiations")

            # Log output state
            logger.info(f"Identified information needs: {information_needs}")
            logger.info(f"Output state: {json.dumps(state.model_dump(), indent=2)}")

            # Add performance metadata
            end_time = datetime.now(UTC)
            trace = add_performance_metadata(
                trace,
                start_time,
                end_time,
                {
                    "information_needs_count": len(information_needs),
                    "state_keys": list(state.__dict__.keys()),
                },
            )

            logger.info("=== Completed identify_information_needs node ===")
            log_state(state, "Output ")
            return InformationNeedsState(
                **{
                    k: v
                    for k, v in state.model_dump().items()
                    if k != "information_needs"
                },
                information_needs=information_needs,
            )
        except Exception as e:
            logger.error(f"Error in identify_information_needs: {str(e)}")
            trace = add_error_metadata(
                trace,
                str(e),
                {"state_keys": list(state.__dict__.keys()) if state else []},
            )
            raise

    return identify_information_needs
