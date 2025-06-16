import logging
from datetime import UTC, datetime
from typing import Callable

from langsmith import traceable

from agents.offer_negotiation.graph.interfaces import RETRIEVE_DOMAIN_KNOWLEDGE_METADATA
from agents.offer_negotiation.graph.state import (
    DomainKnowledgeState,
    InformationNeedsState,
)
from agents.offer_negotiation.graph.utils import log_state
from agents.offer_negotiation.knowledge.domain_knowledge_base import DomainKnowledgeBase
from agents.offer_negotiation.utils.trace_metadata import (
    add_error_metadata,
    add_performance_metadata,
    create_trace_metadata,
)

logger = logging.getLogger(__name__)


def create_retrieve_domain_knowledge_node(
    knowledge_base: DomainKnowledgeBase,
) -> Callable:
    """Create a node that retrieves relevant domain knowledge based on information needs."""

    @traceable(
        name=RETRIEVE_DOMAIN_KNOWLEDGE_METADATA.name,
        run_type="chain",
        metadata=RETRIEVE_DOMAIN_KNOWLEDGE_METADATA.model_dump(),
    )
    def retrieve_domain_knowledge(state: InformationNeedsState) -> DomainKnowledgeState:
        """Retrieve relevant domain knowledge for the negotiation strategy."""
        try:
            logger.info("=== Starting retrieve_domain_knowledge node ===")
            log_state(state, "Input ")

            # Create trace metadata
            start_time = datetime.now(UTC)
            trace = create_trace_metadata("retrieve_domain_knowledge", state)

            # Validate required fields
            if not state.information_needs:
                raise ValueError("Missing required field: information_needs")

            # Retrieve knowledge chunks for each information need
            domain_knowledge = []
            for need in state.information_needs:
                chunks = knowledge_base.retrieve(need)
                domain_knowledge.extend(chunks)

            # Log output state
            logger.info(f"Retrieved {len(domain_knowledge)} domain knowledge chunks")

            # Add performance metadata
            end_time = datetime.now(UTC)
            trace = add_performance_metadata(
                trace,
                start_time,
                end_time,
                {
                    "knowledge_chunks_count": len(domain_knowledge),
                    "information_needs_processed": len(state.information_needs),
                },
            )

            logger.info("=== Completed retrieve_domain_knowledge node ===")
            log_state(state, "Output ")
            return DomainKnowledgeState(
                **{
                    k: v
                    for k, v in state.model_dump().items()
                    if k != "domain_knowledge"
                },
                domain_knowledge=domain_knowledge,
            )
        except Exception as e:
            logger.error(f"Error in retrieve_domain_knowledge: {str(e)}")
            trace = add_error_metadata(
                trace,
                str(e),
                {"state_keys": list(state.__dict__.keys()) if state else []},
            )
            raise

    return retrieve_domain_knowledge
