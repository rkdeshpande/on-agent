import logging
from datetime import UTC, datetime
from typing import Callable

from langsmith import traceable

from agents.offer_negotiation.graph.state import AgentState
from agents.offer_negotiation.graph.utils import log_state
from agents.offer_negotiation.knowledge.domain_documents import DocumentType
from agents.offer_negotiation.knowledge.domain_knowledge_base import DomainKnowledgeBase
from agents.offer_negotiation.utils.trace_metadata import (
    add_error_metadata,
    add_performance_metadata,
    create_trace_metadata,
)

logger = logging.getLogger(__name__)


def create_fetch_domain_knowledge_node(knowledge_base: DomainKnowledgeBase) -> Callable:
    """Create a node that retrieves relevant domain knowledge chunks."""

    @traceable(
        name="fetch_domain_knowledge",
        run_type="chain",
    )
    def fetch_domain_knowledge(state: AgentState) -> AgentState:
        """Fetch relevant domain knowledge based on deal context."""
        # Create trace metadata
        start_time = datetime.now(UTC)
        trace = create_trace_metadata("fetch_domain_knowledge", state)

        try:
            logger.info("=== Starting fetch_domain_knowledge node ===")
            log_state(state, "Input ")

            # Validate required fields
            if not state.deal_context:
                raise ValueError(
                    "Required field 'deal_context' missing from input state"
                )

            # For now, we'll fetch all chunks of each type
            # In a real implementation, this would be more selective based on deal context
            chunks = []
            for doc_type in DocumentType:
                doc_chunks = knowledge_base.get_chunks_by_type(doc_type)
                chunks.extend(doc_chunks)
                logger.info(
                    f"Fetched {len(doc_chunks)} chunks for document type: {doc_type.value}"
                )

            # Update state with domain knowledge
            state.domain_knowledge = chunks

            # Add performance metadata
            end_time = datetime.now(UTC)
            trace = add_performance_metadata(
                trace,
                start_time,
                end_time,
                {
                    "total_chunks_fetched": len(chunks),
                    "document_types": [doc_type.value for doc_type in DocumentType],
                    "domain_knowledge_fetched": True,
                },
            )

            logger.info("=== Completed fetch_domain_knowledge node ===")
            log_state(state, "Output ")

            return state

        except Exception as e:
            logger.error(f"Error in fetch_domain_knowledge: {str(e)}")
            trace = add_error_metadata(
                trace,
                str(e),
                {"state_keys": list(state.__dict__.keys()) if state else []},
            )
            raise

    return fetch_domain_knowledge
