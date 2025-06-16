import json
import logging
from datetime import UTC, datetime
from typing import Callable

from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from agents.offer_negotiation.graph.interfaces import EXPLAIN_RATIONALE_METADATA
from agents.offer_negotiation.graph.state import FinalState, StrategyState
from agents.offer_negotiation.graph.utils import log_state
from agents.offer_negotiation.utils.model import get_llm
from agents.offer_negotiation.utils.prompt_loader import load_prompt
from agents.offer_negotiation.utils.trace_metadata import (
    add_error_metadata,
    add_performance_metadata,
    create_trace_metadata,
)

logger = logging.getLogger(__name__)


def generate_rationale(strategy: str, decision_basis: list) -> str:
    """Generate a rationale string based on the strategy and decision basis."""
    rationale = (
        f"Rationale for the proposed strategy:\n\n{strategy}\n\nDecision Basis:\n"
    )
    for decision in decision_basis:
        rationale += f"- {decision.get('heuristic', '')}: {decision.get('justification', '')} (Confidence: {decision.get('confidence', '')})\n"
    return rationale


def create_explain_rationale_node() -> Callable:
    """Create a node that explains the rationale behind the strategy."""

    @traceable(
        name=EXPLAIN_RATIONALE_METADATA.name,
        run_type="chain",
        metadata=EXPLAIN_RATIONALE_METADATA.model_dump(),
    )
    def explain_rationale(state: StrategyState) -> FinalState:
        """Explain the rationale behind the negotiation strategy."""
        # Create trace metadata
        start_time = datetime.now(UTC)
        trace = create_trace_metadata("explain_rationale", state)

        try:
            logger.info("=== Starting explain_rationale node ===")
            log_state(state, "Input ")

            # Validate required fields
            if not state.strategy:
                raise ValueError("strategy is required")
            if not state.decision_basis:
                raise ValueError("decision_basis is required")

            # Generate rationale based on strategy and decision_basis
            rationale = generate_rationale(state.strategy, state.decision_basis)

            # Log output state
            logger.info(f"Generated rationale: {rationale}")
            log_state(state, "Output ")

            # Add performance metadata
            end_time = datetime.now(UTC)
            trace = add_performance_metadata(
                trace,
                start_time,
                end_time,
                {
                    "rationale_length": len(rationale),
                    "decision_basis_count": len(state.decision_basis),
                },
            )

            logger.info("=== Completed explain_rationale node ===")
            return FinalState(
                **{
                    k: v
                    for k, v in state.model_dump().items()
                    if k not in ["rationale", "reasoning_steps"]
                },
                rationale=rationale,
                reasoning_steps=[rationale],
            )
        except Exception as e:
            logger.error(f"Error in explain_rationale: {str(e)}")
            trace = add_error_metadata(
                trace,
                str(e),
                {"state_keys": list(state.__dict__.keys()) if state else []},
            )
            raise

    return explain_rationale
