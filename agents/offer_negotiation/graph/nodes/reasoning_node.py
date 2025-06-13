import logging
from typing import Callable, Dict, List, Set, TypedDict

from agents.offer_negotiation.core.models.deal_models import DealContext
from agents.offer_negotiation.knowledge.domain_documents import (
    DocumentChunk,
    DocumentType,
)

logger = logging.getLogger(__name__)


class ReasoningOutput(TypedDict):
    """Output from the reasoning node."""

    strategy: str
    rationale: str
    used_deal_fields: Set[str]
    used_domain_chunks: List[Dict[str, str]]
    reasoning_steps: List[str]


def create_reasoning_node() -> Callable:
    """Create a reasoning node that processes deal context and domain knowledge."""

    def reason(state: Dict) -> Dict:
        """
        Process deal context and domain knowledge to generate a strategy.

        Args:
            state: Current state containing deal_context and domain_chunks

        Returns:
            Updated state with reasoning output
        """
        logger.info("=== Starting reasoning node ===")
        logger.debug(f"Input state: {state}")

        # Extract inputs
        deal_context = DealContext(**state["deal_context"])
        domain_chunks = [DocumentChunk(**chunk) for chunk in state["domain_chunks"]]

        logger.info(f"Processing deal context: {deal_context}")
        logger.info(f"Processing {len(domain_chunks)} domain chunks")

        # Track what information we use
        used_deal_fields: Set[str] = set()
        used_domain_chunks: List[Dict[str, str]] = []

        # Example reasoning process (replace with actual LLM call)
        strategy_parts = []
        rationale_parts = []

        # Use deal context
        if deal_context.submission.risk_profile:
            used_deal_fields.add("submission.risk_profile")
            strategy_parts.append(
                f"Risk Profile: {deal_context.submission.risk_profile}"
            )

        if deal_context.negotiation_context.objections:
            used_deal_fields.add("negotiation_context.objections")
            rationale_parts.append("Addressing client objections:")
            for objection in deal_context.negotiation_context.objections:
                rationale_parts.append(f"- {objection}")

        # Use domain knowledge
        for chunk in domain_chunks:
            # Example: Use chunks that mention "premium" if we have premium-related objections
            if "premium" in chunk.text.lower() and any(
                "premium" in obj.lower()
                for obj in deal_context.negotiation_context.objections
            ):
                used_domain_chunks.append(
                    {
                        "chunk_id": chunk.chunk_id,
                        "type": chunk.metadata["document_type"],
                        "reason": "Relevant to premium objections",
                    }
                )
                strategy_parts.append(f"From {chunk.metadata['source_name']}:")
                strategy_parts.append(chunk.text)

        # Combine outputs
        strategy = "\n".join(strategy_parts)
        rationale = "\n".join(rationale_parts)

        logger.info(f"Generated strategy: {strategy}")
        logger.info(f"Generated rationale: {rationale}")

        # Create reasoning output
        reasoning_output: ReasoningOutput = {
            "strategy": strategy,
            "rationale": rationale,
            "used_deal_fields": used_deal_fields,
            "used_domain_chunks": used_domain_chunks,
        }

        # Update state
        updated_state = {
            **state,
            "reasoning_output": reasoning_output,
            "reasoning_steps": state.get("reasoning_steps", [])
            + [
                f"Fetched initial context for deal {deal_context.submission.deal_id}",
                f"Identified {len(used_deal_fields)} information needs: {', '.join(used_deal_fields)}",
                f"Gathered {len(used_domain_chunks)} relevant knowledge chunks",
                "Evaluation: Sufficient information",
                "Gaps identified: None",
                f"Generated strategy using {len(used_deal_fields)} deal fields and {len(used_domain_chunks)} domain chunks",
            ],
        }

        logger.info("=== Completed reasoning node ===")
        logger.debug(f"Output state: {updated_state}")

        return updated_state

    return reason
