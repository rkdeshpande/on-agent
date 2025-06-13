from typing import Any, Dict, List, Optional, Set, TypedDict

from agents.offer_negotiation.core.models.deal_models import DealContext
from agents.offer_negotiation.knowledge.domain_documents import DocumentChunk


class BaseState(TypedDict):
    """Base state shared across all nodes."""

    deal_id: str
    error: Optional[str]  # For error tracking


class DealContextState(BaseState):
    """State for deal context node."""

    deal_context: Optional[Dict[str, Any]]  # Will be populated with DealContext data

    def validate(self) -> bool:
        """Validate that required fields are present."""
        return bool(self.get("deal_id") and self.get("deal_context"))


class InformationNeedsState(DealContextState):
    """State for information needs node."""

    information_needs: List[str]  # List of fields we need to focus on

    def validate(self) -> bool:
        """Validate that required fields are present."""
        return super().validate() and bool(self.get("information_needs"))


class DomainKnowledgeState(InformationNeedsState):
    """State for domain knowledge node."""

    domain_chunks: List[Dict[str, Any]]  # List of relevant DocumentChunks
    used_domain_chunks: List[Dict[str, str]]  # Which chunks were used and why

    def validate(self) -> bool:
        """Validate that required fields are present."""
        return super().validate() and bool(self.get("domain_chunks"))


class StrategyState(DomainKnowledgeState):
    """State for strategy generation node."""

    strategy: str  # The generated strategy
    used_deal_fields: Set[str]  # Which deal fields were used

    def validate(self) -> bool:
        """Validate that required fields are present."""
        return super().validate() and bool(self.get("strategy"))


class FinalState(StrategyState):
    """Final state with complete reasoning output."""

    rationale: str  # Explanation of the strategy
    reasoning_steps: List[str]  # Step-by-step reasoning process

    def validate(self) -> bool:
        """Validate that required fields are present."""
        return super().validate() and bool(
            self.get("rationale") and self.get("reasoning_steps")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to a dictionary for output."""
        return {
            "deal_id": self["deal_id"],
            "strategy": self["strategy"],
            "rationale": self["rationale"],
            "reasoning_steps": self["reasoning_steps"],
            "used_domain_chunks": self["used_domain_chunks"],
            "used_deal_fields": list(self["used_deal_fields"]),
        }
