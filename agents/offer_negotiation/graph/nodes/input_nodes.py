from typing import Annotated, Dict, List, TypedDict

from langgraph.graph import END, StateGraph

from ...core.repositories.mock_deal_repository import MockDealRepository
from ...knowledge.domain_documents import DocumentChunk, DocumentType
from ...knowledge.domain_knowledge_base import DomainKnowledgeBase
from .reasoning_node import ReasoningOutput, create_reasoning_node


# Define our state type
class AgentState(TypedDict):
    deal_id: str
    deal_context: Dict  # Will be populated by deal context node
    domain_chunks: List[DocumentChunk]  # Will be populated by domain knowledge node
    reasoning_steps: List[str]  # For tracking agent's thought process
    reasoning_output: ReasoningOutput  # Will be populated by reasoning node


def create_deal_context_node(repo: MockDealRepository):
    """Create a node that fetches deal context from the repository."""

    def fetch_deal_context(state: AgentState) -> AgentState:
        """Fetch deal context for the given deal_id."""
        deal_id = state["deal_id"]
        deal_context = repo.get_deal_context(deal_id)

        if not deal_context:
            raise ValueError(f"No deal context found for deal_id: {deal_id}")

        return {**state, "deal_context": deal_context.model_dump()}

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

        return {**state, "domain_chunks": [chunk.model_dump() for chunk in chunks]}

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
