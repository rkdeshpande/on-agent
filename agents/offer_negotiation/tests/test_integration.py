import pytest

from agents.offer_negotiation.core.models.deal_models import DealContext
from agents.offer_negotiation.graph.nodes.generate_strategy_node import (
    create_generate_strategy_node,
)
from agents.offer_negotiation.graph.state import DomainKnowledgeState


@pytest.fixture
def sample_deal_context():
    return {
        "submission": {
            "deal_id": "TEST123",
            "coverage_terms": "Commercial Property: $5M limit, $50K deductible",
            "risk_profile": "Low-risk office building",
            "premium_structure": "Annual premium: $120K, Monthly payments",
            "line_of_business": "Commercial Property",
            "territory": "Northeast",
        },
        "client_history": {
            "client_id": "CLIENT456",
            "prior_negotiations": ["2023 Renewal: Accepted $5K deductible increase"],
            "relationship_notes": "Client since 2021, excellent payment history",
            "claim_summary": "No claims in past 3 years",
        },
        "negotiation_context": {
            "deal_id": "TEST123",
            "discussion_notes": ["Initial meeting: Client concerned about premium"],
            "offers": ["Initial offer: $120K premium, $50K deductible"],
            "objections": ["Premium seems high for the coverage"],
        },
        "comparable_deals": [
            {
                "reference_deal_id": "DEAL789",
                "similarity_reason": "Similar office building",
                "outcome_summary": "Negotiated to $110K premium with $60K deductible",
            }
        ],
    }


@pytest.fixture
def sample_domain_knowledge():
    return [
        {
            "text": "Premium adjustments may be considered for clients with good payment history.",
            "metadata": {"document_type": "policy_guidelines"},
        },
        {
            "text": "Deductible adjustments can be used to offset premium increases.",
            "metadata": {"document_type": "negotiation_strategy"},
        },
    ]


def test_strategy_generation_basic(sample_deal_context, sample_domain_knowledge):
    """Test basic strategy generation with a simple premium objection scenario."""
    # Create the strategy generation node
    strategy_node = create_generate_strategy_node()

    # Prepare the input state
    state: DomainKnowledgeState = {
        "deal_context": sample_deal_context,
        "domain_chunks": sample_domain_knowledge,
    }

    # Generate strategy
    result = strategy_node(state)

    # Basic validation
    assert "strategy" in result
    assert isinstance(result["strategy"], str)
    assert len(result["strategy"]) > 0

    # Check for key components in the strategy
    strategy_text = result["strategy"].lower()
    assert "premium" in strategy_text
    assert "deductible" in strategy_text
    assert "strategy" in strategy_text
    assert "rationale" in strategy_text


def test_strategy_generation_with_heuristics(
    sample_deal_context, sample_domain_knowledge
):
    """Test strategy generation with explicit heuristics."""
    strategy_node = create_generate_strategy_node()

    # Add explicit heuristics to the state
    state: DomainKnowledgeState = {
        "deal_context": sample_deal_context,
        "domain_chunks": sample_domain_knowledge,
        "decision_rules": [
            {
                "heuristic": "Premium Objection → Deductible Trade",
                "justification": "Client has history of accepting deductible adjustments",
                "confidence": "High",
            }
        ],
    }

    # Generate strategy
    result = strategy_node(state)

    # Validate heuristic incorporation
    strategy_text = result["strategy"].lower()
    assert "premium objection" in strategy_text
    assert "deductible trade" in strategy_text
    assert "confidence" in strategy_text
