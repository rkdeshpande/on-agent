import pytest

from agents.offer_negotiation.core.models.deal_models import DealContext
from agents.offer_negotiation.graph.nodes.generate_strategy_node import (
    create_generate_strategy_node,
)
from agents.offer_negotiation.graph.state import DomainKnowledgeState


@pytest.fixture
def premium_objection_deal():
    """Create a deal context specifically designed to test premium objection handling."""
    return {
        "submission": {
            "deal_id": "PREMIUM123",
            "coverage_terms": "Commercial Property: $10M limit, $100K deductible",
            "risk_profile": "Medium-risk manufacturing facility",
            "premium_structure": "Annual premium: $250K, Quarterly payments",
            "line_of_business": "Commercial Property",
            "territory": "Midwest",
        },
        "client_history": {
            "client_id": "CLIENT789",
            "prior_negotiations": [
                "2022 Renewal: Accepted $15K deductible increase",
                "2021 Renewal: Negotiated 8% premium reduction",
            ],
            "relationship_notes": "Client since 2019, consistent payment history",
            "claim_summary": "One minor claim in 2020",
        },
        "negotiation_context": {
            "deal_id": "PREMIUM123",
            "discussion_notes": [
                "Initial meeting: Client concerned about premium increase",
                "Follow-up: Client mentioned cash flow constraints",
            ],
            "offers": ["Initial offer: $250K premium, $100K deductible"],
            "objections": [
                "Premium increase is too high",
                "Quarterly payments are challenging",
            ],
        },
        "comparable_deals": [
            {
                "reference_deal_id": "DEAL456",
                "similarity_reason": "Similar manufacturing facility",
                "outcome_summary": "Negotiated to $230K premium with $120K deductible",
            }
        ],
    }


@pytest.fixture
def premium_domain_knowledge():
    """Create domain knowledge specific to premium objections."""
    return [
        {
            "text": "Premium objections can be addressed through deductible adjustments and payment structure flexibility.",
            "metadata": {"document_type": "negotiation_strategy"},
        },
        {
            "text": "Clients with good payment history may be eligible for premium reductions.",
            "metadata": {"document_type": "policy_guidelines"},
        },
        {
            "text": "Payment structure flexibility can help address cash flow concerns.",
            "metadata": {"document_type": "client_guidelines"},
        },
    ]


def test_few_shot_premium_objection(premium_objection_deal, premium_domain_knowledge):
    """Test strategy generation with the few-shot example for premium objections."""
    strategy_node = create_generate_strategy_node()

    state: DomainKnowledgeState = {
        "deal_context": premium_objection_deal,
        "domain_chunks": premium_domain_knowledge,
    }

    result = strategy_node(state)
    strategy_text = result["strategy"].lower()

    # Test structure following few-shot example
    assert "deal context summary" in strategy_text
    assert "key objections" in strategy_text
    assert "domain rules used" in strategy_text
    assert "strategy" in strategy_text
    assert "rationale" in strategy_text
    assert "expected outcome" in strategy_text

    # Test specific content requirements
    assert "premium adjustment" in strategy_text
    assert "deductible trade-off" in strategy_text
    assert "payment structure" in strategy_text

    # Test justification requirements
    justifications = [
        "client's history",
        "client's good payment history",
        "client has demonstrated acceptance",
        "client history",
    ]
    assert any(j in strategy_text for j in justifications)
    assert "comparable deal" in strategy_text

    # Test value specificity
    assert "$" in strategy_text  # Should include specific dollar amounts
    assert "%" in strategy_text  # Should include percentage changes


def test_few_shot_structured_output(premium_objection_deal, premium_domain_knowledge):
    """Test that the output follows the structured format from the few-shot example."""
    strategy_node = create_generate_strategy_node()

    state: DomainKnowledgeState = {
        "deal_context": premium_objection_deal,
        "domain_chunks": premium_domain_knowledge,
    }

    result = strategy_node(state)
    strategy_text = result["strategy"]

    # Test section formatting
    sections = strategy_text.split("\n\n")
    assert len(sections) >= 5  # Should have at least 5 major sections

    # Test bullet point formatting
    assert "- " in strategy_text or "* " in strategy_text

    # Test numerical list formatting
    assert "1." in strategy_text
    assert "2." in strategy_text

    # Test indentation for subsections
    assert "    - " in strategy_text or "    * " in strategy_text


def test_few_shot_coverage_request():
    """Test strategy generation with the few-shot example for a coverage request objection."""
    strategy_node = create_generate_strategy_node()
    deal_context = {
        "submission": {
            "deal_id": "COVREQ001",
            "coverage_terms": "Commercial Property: $12M limit, $100K deductible",
            "risk_profile": "Low-risk office park",
            "premium_structure": "Annual premium: $200K, Annual payments",
            "line_of_business": "Commercial Property",
            "territory": "Midwest",
        },
        "client_history": {
            "client_id": "CLIENTCOV1",
            "prior_negotiations": ["2023: Requested flood coverage, not available"],
            "relationship_notes": "Client since 2018, good payment history",
            "claim_summary": "No major claims",
        },
        "negotiation_context": {
            "deal_id": "COVREQ001",
            "discussion_notes": [
                "Client wants flood and higher business interruption limits"
            ],
            "offers": ["Initial offer: $200K premium, $100K deductible"],
            "objections": [
                "Request for flood coverage",
                "Request for $3M business interruption limit",
            ],
        },
        "comparable_deals": [
            {
                "reference_deal_id": "COVDEAL002",
                "similarity_reason": "Similar office park",
                "outcome_summary": "Included $1M flood sublimit, $2.5M business interruption limit",
            }
        ],
    }
    domain_knowledge = [
        {
            "text": "Flood coverage is subject to underwriting and may be capped.",
            "metadata": {"document_type": "policy_guidelines"},
        },
        {
            "text": "Business interruption limits are capped at $2.5M for low-risk office parks.",
            "metadata": {"document_type": "policy_guidelines"},
        },
    ]
    state: DomainKnowledgeState = {
        "deal_context": deal_context,
        "domain_chunks": domain_knowledge,
    }
    result = strategy_node(state)
    strategy_text = result["strategy"].lower()
    # Structure checks
    assert "deal context summary" in strategy_text
    assert "key objections" in strategy_text
    assert "domain rules used" in strategy_text
    assert "strategy" in strategy_text
    assert "rationale" in strategy_text
    assert "expected outcome" in strategy_text
    # Content checks
    assert "flood coverage" in strategy_text
    assert "business interruption" in strategy_text
    assert "sublimit" in strategy_text or "$1m" in strategy_text
    assert "cap" in strategy_text or "maximum" in strategy_text
    assert "comparable deal" in strategy_text or "covdeal002" in strategy_text


def test_few_shot_high_risk():
    """Test strategy generation with the few-shot example for a high-risk scenario."""
    strategy_node = create_generate_strategy_node()
    deal_context = {
        "submission": {
            "deal_id": "HIGHRISK01",
            "coverage_terms": "Manufacturing: $20M limit, $500K deductible",
            "risk_profile": "High-risk chemical plant",
            "premium_structure": "Annual premium: $1.2M, Annual payments",
            "line_of_business": "Manufacturing",
            "territory": "Southwest",
        },
        "client_history": {
            "client_id": "CLIENTHR1",
            "prior_negotiations": ["2022: Required additional safety audits"],
            "relationship_notes": "Client since 2015, some compliance issues",
            "claim_summary": "One major claim in 2021",
        },
        "negotiation_context": {
            "deal_id": "HIGHRISK01",
            "discussion_notes": ["Client objects to high premium and deductible"],
            "offers": ["Initial offer: $1.2M premium, $500K deductible"],
            "objections": ["Premium is too high", "Deductible is too high"],
        },
        "comparable_deals": [
            {
                "reference_deal_id": "HRDEAL03",
                "similarity_reason": "Similar chemical plant",
                "outcome_summary": "$1.18M premium, $450K deductible, required safety audits",
            }
        ],
    }
    domain_knowledge = [
        {
            "text": "High-risk manufacturing requires strict terms and enhanced safety protocols.",
            "metadata": {"document_type": "risk_guidelines"},
        },
        {
            "text": "Premium and deductible flexibility is limited for high-risk clients.",
            "metadata": {"document_type": "negotiation_strategy"},
        },
    ]
    state: DomainKnowledgeState = {
        "deal_context": deal_context,
        "domain_chunks": domain_knowledge,
    }
    result = strategy_node(state)
    strategy_text = result["strategy"].lower()
    # Structure checks
    assert "deal context summary" in strategy_text
    assert "key objections" in strategy_text
    assert "domain rules used" in strategy_text
    assert "strategy" in strategy_text
    assert "rationale" in strategy_text
    assert "expected outcome" in strategy_text
    # Content checks
    assert "high-risk" in strategy_text or "high risk" in strategy_text
    assert "safety" in strategy_text
    assert "premium adjustment" in strategy_text
    assert "deductible adjustment" in strategy_text
    assert "risk profile" in strategy_text
    assert "comparable deal" in strategy_text or "hrdeal03" in strategy_text
