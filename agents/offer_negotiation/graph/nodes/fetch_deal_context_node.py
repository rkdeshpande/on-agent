import logging
from datetime import UTC, datetime
from typing import Callable

from langsmith import traceable

from agents.offer_negotiation.core.repositories.mock_deal_repository import (
    MockDealRepository,
)
from agents.offer_negotiation.graph.state import AgentState
from agents.offer_negotiation.graph.utils import log_state
from agents.offer_negotiation.utils.trace_metadata import (
    add_error_metadata,
    add_performance_metadata,
    create_trace_metadata,
)

logger = logging.getLogger(__name__)


def create_fetch_deal_context_node(deal_repo: MockDealRepository) -> Callable:
    """Create a node that fetches deal context from the repository."""

    @traceable(
        name="fetch_deal_context",
        run_type="chain",
    )
    def fetch_deal_context(state: AgentState) -> AgentState:
        """Fetch deal context for the given deal_id."""
        # Create trace metadata
        start_time = datetime.now(UTC)
        trace = create_trace_metadata("fetch_deal_context", state)

        try:
            logger.info("=== Starting fetch_deal_context node ===")
            log_state(state, "Input ")

            # Validate required fields
            if not state.deal_id:
                raise ValueError("Required field 'deal_id' missing from input state")

            # Fetch deal context from repository
            deal_context = deal_repo.get_deal_context(state.deal_id)

            if not deal_context:
                raise ValueError(f"No deal context found for deal_id: {state.deal_id}")

            # Update state with deal context
            state.deal_context = deal_context.model_dump()

            # Add performance metadata
            end_time = datetime.now(UTC)
            trace = add_performance_metadata(
                trace,
                start_time,
                end_time,
                {
                    "deal_id": state.deal_id,
                    "deal_context_fetched": True,
                },
            )

            logger.info("=== Completed fetch_deal_context node ===")
            log_state(state, "Output ")

            return state

        except Exception as e:
            logger.error(f"Error in fetch_deal_context: {str(e)}")
            trace = add_error_metadata(
                trace,
                str(e),
                {"state_keys": list(state.__dict__.keys()) if state else []},
            )
            raise

    return fetch_deal_context
