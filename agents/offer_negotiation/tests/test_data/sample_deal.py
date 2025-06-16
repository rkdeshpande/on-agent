"""Sample deal data for testing AIP execution."""

SAMPLE_DEAL = {
    "deal_id": "DEAL001",
    "submission": {
        "deal_id": "DEAL001",
        "coverage_terms": "Commercial Property: $10M limit, $100K deductible",
        "risk_profile": "Medium-risk manufacturing facility",
        "premium_structure": "Annual premium: $500K, Quarterly payments",
        "line_of_business": "Manufacturing",
        "territory": "Northeast",
    },
    "client_history": {
        "client_id": "CLIENT001",
        "prior_negotiations": [
            "2022: Accepted 10% premium increase with deductible adjustment",
            "2021: Requested additional coverage for business interruption",
        ],
        "relationship_notes": "Client since 2018, good payment history",
        "claim_summary": "No major claims in past 3 years",
    },
    "negotiation_context": {
        "deal_id": "DEAL001",
        "discussion_notes": [
            "Client concerned about premium increase",
            "Interested in exploring deductible options",
        ],
        "offers": [
            "Initial offer: $500K premium, $100K deductible",
            "Counter offer: $450K premium, $150K deductible",
        ],
        "objections": [
            "Premium increase is too high",
            "Would like to explore higher deductible options",
        ],
    },
    "comparable_deals": [
        {
            "reference_deal_id": "REF001",
            "similarity_reason": "Similar manufacturing facility",
            "outcome_summary": "$480K premium, $125K deductible, quarterly payments",
        },
        {
            "reference_deal_id": "REF002",
            "similarity_reason": "Similar risk profile",
            "outcome_summary": "$460K premium, $150K deductible, quarterly payments",
        },
    ],
}
