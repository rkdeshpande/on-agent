import json
import logging
from datetime import UTC, datetime
from typing import Any, Callable, Dict, List, Optional, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from agents.offer_negotiation.core.models.deal_models import DealContext
from agents.offer_negotiation.graph.interfaces import GENERATE_STRATEGY_METADATA
from agents.offer_negotiation.graph.state import AgentState
from agents.offer_negotiation.graph.utils import log_state
from agents.offer_negotiation.knowledge.domain_documents import DocumentChunk
from agents.offer_negotiation.utils.model import get_llm
from agents.offer_negotiation.utils.prompt_loader import load_prompt
from agents.offer_negotiation.utils.trace_metadata import (
    add_error_metadata,
    add_performance_metadata,
    create_trace_metadata,
)

logger = logging.getLogger(__name__)


class DecisionBasis(TypedDict):
    heuristic: str
    justification: str
    confidence: str


def evaluate_heuristics(deal_context: DealContext) -> List[DecisionBasis]:
    """Evaluate deal context against defined heuristics and return matching decisions."""
    decisions: List[DecisionBasis] = []

    # Heuristic 1: Premium Objection → Deductible Trade
    if any(
        "premium" in obj.lower() for obj in deal_context.negotiation_context.objections
    ):
        # Check if client has history of accepting deductible adjustments
        has_deductible_history = any(
            "deductible" in note.lower()
            for note in deal_context.client_history.prior_negotiations
        )

        if has_deductible_history:
            decisions.append(
                {
                    "heuristic": "Premium Objection → Deductible Trade",
                    "justification": "Client objected to premium and has history of accepting deductible adjustments",
                    "confidence": "High - Matches objection pattern and client history",
                }
            )

    # Heuristic 2: Coverage Request → Evaluate Against Limits
    if any(
        "coverage" in obj.lower() for obj in deal_context.negotiation_context.objections
    ):
        # Extract current limits from coverage terms
        try:
            # Parse coverage terms to get current limits
            coverage_terms = deal_context.submission.coverage_terms.lower()
            if "limit" in coverage_terms:
                # limit_str = coverage_terms.split("$")[1].split()[0]
                # current_limit = float(limit_str.replace("m", "000000"))

                # Check for specific coverage requests in objections
                for objection in deal_context.negotiation_context.objections:
                    if "business interruption" in objection.lower():
                        decisions.append(
                            {
                                "heuristic": "Coverage Request → Business Interruption",
                                "justification": "Client requested additional business interruption coverage",
                                "confidence": "High - Explicit coverage request",
                            }
                        )
                    elif "flood" in objection.lower():
                        decisions.append(
                            {
                                "heuristic": "Coverage Request → Flood Coverage",
                                "justification": "Client requested flood coverage consideration",
                                "confidence": "High - Explicit coverage request",
                            }
                        )
        except (IndexError, ValueError):
            logger.warning("Could not parse coverage limits from terms")

    # Heuristic 3: Risk Profile → Coverage Adjustments
    if deal_context.submission.risk_profile:
        risk_profile = deal_context.submission.risk_profile.lower()
        if "high-risk" in risk_profile:
            decisions.append(
                {
                    "heuristic": "High Risk → Enhanced Coverage",
                    "justification": "High-risk profile suggests need for enhanced coverage options",
                    "confidence": "Medium - Based on risk profile",
                }
            )

    return decisions


def create_generate_strategy_node() -> Callable:
    """Create a node that generates a negotiation strategy based on deal context and domain knowledge."""
    # Get the LLM
    llm = get_llm()

    # Create the prompt template
    strategy_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", load_prompt("strategy_generation.md")),
            (
                "human",
                "Please generate a negotiation strategy based on the provided context and decision rules.",
            ),
        ]
    )

    @traceable(
        name=GENERATE_STRATEGY_METADATA.name,
        run_type="chain",
        metadata=GENERATE_STRATEGY_METADATA.model_dump(),
    )
    def generate_strategy(state: AgentState) -> AgentState:
        """Generate a negotiation strategy based on domain knowledge."""
        # Create trace metadata
        trace = create_trace_metadata(GENERATE_STRATEGY_METADATA.name, state)

        try:
            logger.info("=== Starting generate_strategy node ===")
            log_state(state, "Input ")

            # Validate required fields
            if not state.deal_context:
                raise ValueError(
                    "Required field 'deal_context' missing from input state"
                )
            if not state.domain_knowledge:
                raise ValueError(
                    "Required field 'domain_knowledge' missing from input state"
                )

            # Extract deal context
            deal_context = DealContext(**state.deal_context)

            # Evaluate heuristics
            decisions = evaluate_heuristics(deal_context)

            # Log triggered heuristics
            for decision in decisions:
                logger.info(
                    f"Triggered heuristic: {decision['heuristic']}\n"
                    f"Justification: {decision['justification']}\n"
                    f"Confidence: {decision['confidence']}"
                )

            # Format domain knowledge
            domain_knowledge = "\n".join(
                [
                    f"- {chunk.text} (Source: {chunk.metadata['document_type']})"
                    for chunk in state.domain_knowledge
                ]
            )

            # Format decision rules for prompt
            decision_rules = (
                "\n".join(
                    [
                        f"- {decision['heuristic']}: {decision['justification']}"
                        for decision in decisions
                    ]
                )
                or "No specific decision rules were triggered."
            )

            # Generate strategy using LLM
            chain = strategy_prompt | llm
            response = chain.invoke(
                {
                    "deal_context": deal_context.model_dump_json(indent=2),
                    "domain_knowledge": domain_knowledge
                    or "No specific domain knowledge available.",
                    "decision_rules": decision_rules,
                }
            )

            negotiation_strategy = response.content
            logger.info(f"Generated strategy: {negotiation_strategy}")

            # Update state with strategy and decision basis
            logger.info("=== Completed generate_strategy node ===")
            state.strategy = negotiation_strategy
            state.decision_basis = decisions
            return state

        except Exception as e:
            # Add error metadata
            trace = add_error_metadata(
                trace,
                e,
                error_context={"state_keys": list(state.__dict__.keys())},
            )
            raise

    return generate_strategy
