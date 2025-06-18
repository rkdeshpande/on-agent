from typing import Dict, List

from langgraph.graph import END, StateGraph

from ...core.repositories.mock_deal_repository import MockDealRepository
from ...knowledge.domain_documents import DocumentChunk, DocumentType
from ...knowledge.domain_knowledge_base import DomainKnowledgeBase
from ..state import AgentState


def create_deal_context_node(repo: MockDealRepository):
    """Create a node that fetches deal context from the repository."""

    def fetch_deal_context(state: AgentState) -> AgentState:
        """Fetch deal context for the given deal_id."""
        deal_id = state.deal_id
        deal_context = repo.get_deal_context(deal_id)

        if not deal_context:
            raise ValueError(f"No deal context found for deal_id: {deal_id}")

        state.deal_context = deal_context.model_dump()
        return state

    return fetch_deal_context


def create_domain_knowledge_node(kb: DomainKnowledgeBase):
    """Create a node that retrieves relevant domain knowledge chunks."""

    def fetch_domain_knowledge(state: AgentState) -> AgentState:
        """Fetch relevant domain knowledge based on deal context."""
        # For now, we'll fetch all chunks of each type
        # In a real implementation, this would be more selective
        chunks = []
        for doc_type in DocumentType:
            chunks.extend(kb.get_chunks_by_type(doc_type))

        state.domain_knowledge = chunks
        return state

    return fetch_domain_knowledge


def create_input_graph(
    deal_repo: MockDealRepository, knowledge_base: DomainKnowledgeBase
) -> StateGraph:
    """Create the input portion of our agent graph."""

    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("fetch_deal_context", create_deal_context_node(deal_repo))
    workflow.add_node(
        "fetch_domain_knowledge", create_domain_knowledge_node(knowledge_base)
    )

    # Define the flow
    workflow.set_entry_point("fetch_deal_context")
    workflow.add_edge("fetch_deal_context", "fetch_domain_knowledge")

    return workflow
