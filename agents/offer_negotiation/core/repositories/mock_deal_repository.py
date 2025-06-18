"""Mock deal repository for testing."""

import json
from pathlib import Path
from typing import Any, Dict

from agents.offer_negotiation.core.models.deal_models import DealContext
from agents.offer_negotiation.tests.test_data.sample_deal import SAMPLE_DEAL
from config.app_config import config


class MockDealRepository:
    """Mock repository for deal data."""

    def __init__(self):
        """Initialize the repository with sample data."""
        # Load DEAL123 from JSON using config path
        deal123_path = config.deals_dir / "DEAL123.json"
        if deal123_path.exists():
            with open(deal123_path, "r") as f:
                deal123 = json.load(f)
        else:
            deal123 = None
        self._deals = {
            "DEAL001": SAMPLE_DEAL,
        }
        if deal123:
            self._deals["DEAL123"] = deal123

    def get_deal(self, deal_id: str) -> Dict[str, Any]:
        """Get a deal by ID.

        Args:
            deal_id: ID of the deal to retrieve

        Returns:
            Deal data as a dictionary

        Raises:
            KeyError: If deal not found
        """
        if deal_id not in self._deals:
            raise KeyError(f"Deal {deal_id} not found")
        return self._deals[deal_id]

    def get_deal_context(self, deal_id: str) -> dict:
        deal = self.get_deal(deal_id)
        if isinstance(deal, dict):
            try:
                return DealContext(**deal)
            except Exception:
                # If the dict is not compatible, just return as is
                return deal
        return deal
