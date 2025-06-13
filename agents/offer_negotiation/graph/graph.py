from langgraph.graph import END, StateGraph

from agents.offer_negotiation.core.repositories.mock_deal_repository import (
    MockDealRepository,
)
from agents.offer_negotiation.graph.nodes.explain_rationale_node import (
    create_explain_rationale_node,
)
from agents.offer_negotiation.graph.nodes.generate_strategy_node import (
    create_generate_strategy_node,
)
from agents.offer_negotiation.graph.nodes.identify_information_needs_node import (
    create_identify_information_needs_node,
)
from agents.offer_negotiation.graph.nodes.input_nodes import create_input_graph
from agents.offer_negotiation.graph.nodes.retrieve_domain_knowledge_node import (
    create_retrieve_domain_knowledge_node,
)
from agents.offer_negotiation.knowledge.domain_knowledge_base import DomainKnowledgeBase


def create_agent_graph(
    deal_repo: MockDealRepository,
    knowledge_base: DomainKnowledgeBase,
) -> StateGraph:
    """Create the complete agent graph with all nodes and edges."""
    # Create the input portion of the graph
    workflow = create_input_graph(deal_repo, knowledge_base)

    # Add our new nodes
    workflow.add_node(
        "identify_information_needs", create_identify_information_needs_node()
    )
    workflow.add_node(
        "retrieve_domain_knowledge",
        create_retrieve_domain_knowledge_node(knowledge_base),
    )
    workflow.add_node("generate_strategy", create_generate_strategy_node())
    workflow.add_node("explain_rationale", create_explain_rationale_node())

    # Connect the nodes in sequence
    workflow.add_edge("fetch_domain_knowledge", "identify_information_needs")
    workflow.add_edge("identify_information_needs", "retrieve_domain_knowledge")
    workflow.add_edge("retrieve_domain_knowledge", "generate_strategy")
    workflow.add_edge("generate_strategy", "explain_rationale")
    workflow.add_edge("explain_rationale", END)

    return workflow
