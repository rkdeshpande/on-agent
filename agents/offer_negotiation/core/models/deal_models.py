from typing import List, Optional

from pydantic import BaseModel, Field


class SubmissionDetails(BaseModel):
    deal_id: str
    coverage_terms: str
    risk_profile: str
    premium_structure: str
    line_of_business: Optional[str] = None
    territory: Optional[str] = None


class ClientHistory(BaseModel):
    client_id: str
    prior_negotiations: List[str]
    relationship_notes: Optional[str] = None
    claim_summary: Optional[str] = None


class NegotiationContext(BaseModel):
    deal_id: str
    discussion_notes: List[str]
    offers: List[str]
    objections: List[str]


class ComparableDealReference(BaseModel):
    reference_deal_id: str
    similarity_reason: str
    outcome_summary: str


class DealContext(BaseModel):
    submission: SubmissionDetails
    client_history: ClientHistory
    negotiation_context: NegotiationContext
    comparable_deals: List[ComparableDealReference]


# Example data for testing
EXAMPLE_SUBMISSION = SubmissionDetails(
    deal_id="DEAL123",
    coverage_terms="Commercial Property: $10M limit, $100K deductible",
    risk_profile="High-risk manufacturing facility in flood zone",
    premium_structure="Annual premium: $250K, Quarterly payments",
    line_of_business="Commercial Property",
    territory="Northeast",
)

EXAMPLE_CLIENT_HISTORY = ClientHistory(
    client_id="CLIENT456",
    prior_negotiations=[
        "2023 Renewal: Negotiated 15% premium reduction",
        "2022 New Business: Accepted initial terms with minor modifications",
    ],
    relationship_notes="Long-term client since 2018, good payment history",
    claim_summary="One major claim in 2021 ($2.5M), no other claims",
)

EXAMPLE_NEGOTIATION_CONTEXT = NegotiationContext(
    deal_id="DEAL123",
    discussion_notes=[
        "Initial meeting: Client concerned about flood coverage",
        "Follow-up: Discussed risk mitigation options",
    ],
    offers=[
        "Initial offer: $250K premium, $100K deductible",
        "Revised offer: $225K premium, $150K deductible",
    ],
    objections=[
        "Premium too high compared to market",
        "Deductible increase not acceptable",
    ],
)

EXAMPLE_COMPARABLE_DEALS = [
    ComparableDealReference(
        reference_deal_id="DEAL789",
        similarity_reason="Similar manufacturing facility in same flood zone",
        outcome_summary="Successfully renewed with 10% premium increase",
    ),
    ComparableDealReference(
        reference_deal_id="DEAL101",
        similarity_reason="Similar coverage limits and risk profile",
        outcome_summary="Negotiated to $200K premium with $125K deductible",
    ),
]

EXAMPLE_DEAL_CONTEXT = DealContext(
    submission=EXAMPLE_SUBMISSION,
    client_history=EXAMPLE_CLIENT_HISTORY,
    negotiation_context=EXAMPLE_NEGOTIATION_CONTEXT,
    comparable_deals=EXAMPLE_COMPARABLE_DEALS,
)

# Test serialization
if __name__ == "__main__":
    # Test each model
    print("Testing SubmissionDetails serialization:")
    print(EXAMPLE_SUBMISSION.model_dump_json(indent=2))
    print("\nTesting ClientHistory serialization:")
    print(EXAMPLE_CLIENT_HISTORY.model_dump_json(indent=2))
    print("\nTesting NegotiationContext serialization:")
    print(EXAMPLE_NEGOTIATION_CONTEXT.model_dump_json(indent=2))
    print("\nTesting ComparableDealReference serialization:")
    print(EXAMPLE_COMPARABLE_DEALS[0].model_dump_json(indent=2))
    print("\nTesting full DealContext serialization:")
    print(EXAMPLE_DEAL_CONTEXT.model_dump_json(indent=2))
