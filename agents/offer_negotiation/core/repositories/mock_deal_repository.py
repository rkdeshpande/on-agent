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
        self._deals = {
            "DEAL001": SAMPLE_DEAL,
        }

        # Load all JSON files from the deals directory
        deals_dir = config.deals_dir
        if deals_dir.exists():
            for json_file in deals_dir.glob("*.json"):
                try:
                    deal_id = json_file.stem  # Get filename without extension
                    with open(json_file, "r") as f:
                        deal_data = json.load(f)
                    self._deals[deal_id] = deal_data
                    print(f"Loaded deal: {deal_id} from {json_file}")
                except Exception as e:
                    print(f"Error loading deal from {json_file}: {e}")

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
