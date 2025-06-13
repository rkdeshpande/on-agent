from agents.offer_negotiation.core.models.deal_models import EXAMPLE_DEAL_CONTEXT
from agents.offer_negotiation.core.repositories.mock_deal_repository import (
    MockDealRepository,
)
from agents.offer_negotiation.graph.nodes.input_nodes import create_input_graph
from agents.offer_negotiation.knowledge.domain_knowledge_base import DomainKnowledgeBase


def test_deal_context_node():
    """Test the deal context node."""
    deal_repo = MockDealRepository()
    knowledge_base = DomainKnowledgeBase()
    graph = create_input_graph(deal_repo, knowledge_base)
    node = graph.compile()

    # Test with valid deal ID
    result = node.invoke({"deal_id": "DEAL123"})
    assert "deal_context" in result
    assert result["deal_context"]["submission"]["deal_id"] == "DEAL123"


def test_domain_knowledge_node():
    """Test the domain knowledge node."""
    deal_repo = MockDealRepository()
    knowledge_base = DomainKnowledgeBase()
    graph = create_input_graph(deal_repo, knowledge_base)
    node = graph.compile()

    # Test with minimal state (must include deal_id)
    result = node.invoke({"deal_id": "DEAL123"})
    assert "domain_chunks" in result
    assert isinstance(result["domain_chunks"], list)
