from langgraph.graph import END, StateGraph

from agents.offer_negotiation.core.repositories.mock_deal_repository import (
    MockDealRepository,
)
from agents.offer_negotiation.graph.nodes.input_nodes import create_input_graph
from agents.offer_negotiation.graph.nodes.reasoning_node import create_reasoning_node
from agents.offer_negotiation.knowledge.domain_knowledge_base import DomainKnowledgeBase


def create_agent_graph(
    deal_repo: MockDealRepository,
    knowledge_base: DomainKnowledgeBase,
) -> StateGraph:
    """Create the complete agent graph with all nodes and edges."""
    # Create the input portion of the graph
    workflow = create_input_graph(deal_repo, knowledge_base)

    # Add the reasoning node
    workflow.add_node("reason", create_reasoning_node())

    # Connect the nodes
    workflow.add_edge("fetch_domain_knowledge", "reason")
    workflow.add_edge("reason", END)

    return workflow
