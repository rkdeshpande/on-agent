import logging
from typing import Callable

from langsmith import traceable

from agents.offer_negotiation.graph.state import (
    DomainKnowledgeState,
    InformationNeedsState,
)
from agents.offer_negotiation.knowledge.domain_documents import DocumentChunk
from agents.offer_negotiation.knowledge.domain_knowledge_base import DomainKnowledgeBase

logger = logging.getLogger(__name__)


def create_retrieve_domain_knowledge_node(kb: DomainKnowledgeBase) -> Callable:
    """Create a node that retrieves relevant domain knowledge based on information needs."""

    @traceable(name="retrieve_domain_knowledge", run_type="chain")
    def retrieve_domain_knowledge(state: InformationNeedsState) -> DomainKnowledgeState:
        logger.info("=== Starting retrieve_domain_knowledge node ===")
        logger.debug(f"Input state: {state}")

        # Retrieve domain chunks based on information needs
        domain_chunks = []
        used_domain_chunks = []

        for need in state["information_needs"]:
            # Example: Retrieve chunks that mention the need
            chunks = kb.search_chunks(need)
            for chunk in chunks:
                domain_chunks.append(chunk.model_dump())
                used_domain_chunks.append(
                    {
                        "chunk_id": chunk.chunk_id,
                        "type": chunk.metadata["document_type"],
                        "reason": f"Relevant to {need}",
                    }
                )

        logger.info(f"Retrieved {len(domain_chunks)} domain chunks")

        # Update state
        updated_state: DomainKnowledgeState = {
            **state,
            "domain_chunks": domain_chunks,
            "used_domain_chunks": used_domain_chunks,
        }

        logger.info("=== Completed retrieve_domain_knowledge node ===")
        logger.debug(f"Output state: {updated_state}")

        return updated_state

    return retrieve_domain_knowledge
