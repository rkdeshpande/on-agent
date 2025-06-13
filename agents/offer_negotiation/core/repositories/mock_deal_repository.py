from typing import Optional

from ..models.deal_models import (
    EXAMPLE_DEAL_CONTEXT,  # We'll use this as our mock data for now
)
from ..models.deal_models import (
    ClientHistory,
    ComparableDealReference,
    DealContext,
    NegotiationContext,
    SubmissionDetails,
)


class MockDealRepository:
    """Mock repository for deal data that could be replaced with real DB access later."""

    def __init__(self):
        # In a real implementation, this would be a DB connection
        self._mock_data = {
            "DEAL123": EXAMPLE_DEAL_CONTEXT,
            # Add more mock deals as needed
        }

    def get_deal_context(self, deal_id: str) -> Optional[DealContext]:
        """
        Retrieve a complete DealContext for a given deal_id.

        Args:
            deal_id: The unique identifier for the deal

        Returns:
            DealContext if found, None if not found
        """
        return self._mock_data.get(deal_id)

    def get_submission_details(self, deal_id: str) -> Optional[SubmissionDetails]:
        """Get just the submission details for a deal."""
        context = self.get_deal_context(deal_id)
        return context.submission if context else None

    def get_client_history(self, client_id: str) -> Optional[ClientHistory]:
        """Get client history for a given client_id."""
        # In a real implementation, this would query by client_id
        # For now, we'll just return the history from our mock deal
        context = self.get_deal_context("DEAL123")
        return context.client_history if context else None

    def get_negotiation_context(self, deal_id: str) -> Optional[NegotiationContext]:
        """Get the current negotiation context for a deal."""
        context = self.get_deal_context(deal_id)
        return context.negotiation_context if context else None

    def get_comparable_deals(self, deal_id: str) -> list[ComparableDealReference]:
        """Get comparable deals for a given deal."""
        context = self.get_deal_context(deal_id)
        return context.comparable_deals if context else []


# Example usage
if __name__ == "__main__":
    repo = MockDealRepository()

    # Test getting full context
    deal_context = repo.get_deal_context("DEAL123")
    print("Full deal context:")
    print(deal_context.model_dump_json(indent=2) if deal_context else "Not found")

    # Test getting individual components
    submission = repo.get_submission_details("DEAL123")
    print("\nSubmission details:")
    print(submission.model_dump_json(indent=2) if submission else "Not found")

    # Test getting non-existent deal
    missing_deal = repo.get_deal_context("NONEXISTENT")
    print("\nNon-existent deal:")
    print("Found" if missing_deal else "Not found")
