from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from agents.offer_negotiation.core.models.deal_models import DealContext
from agents.offer_negotiation.knowledge.domain_documents import DocumentChunk


class BaseState(BaseModel):
    """Base state shared across all nodes."""

    deal_id: str
    error: Optional[str] = None  # For error tracking


class DealContextState(BaseState):
    """State for deal context node."""

    deal_context: Optional[
        Dict[str, Any]
    ] = None  # Will be populated with DealContext data
    domain_knowledge: List[DocumentChunk] = Field(default_factory=list)
    reasoning_steps: List[str] = Field(default_factory=list)
    reasoning_output: Dict[str, Any] = Field(default_factory=dict)


class InformationNeedsState(DealContextState):
    """State for information needs node."""

    information_needs: List[str] = Field(
        default_factory=list
    )  # List of fields we need to focus on


class DomainKnowledgeState(InformationNeedsState):
    """State for domain knowledge node."""

    used_domain_chunks: List[Dict[str, str]] = Field(
        default_factory=list
    )  # Which chunks were used and why


class StrategyState(DomainKnowledgeState):
    """State for strategy generation node."""

    strategy: Optional[str] = None  # The generated strategy
    used_deal_fields: Set[str] = Field(
        default_factory=set
    )  # Which deal fields were used
    decision_basis: List[Dict[str, str]] = Field(
        default_factory=list
    )  # Which heuristics were triggered and why


class FinalState(StrategyState):
    """Final state with complete reasoning output."""

    rationale: Optional[str] = None  # Explanation of the strategy

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to a dictionary for output."""
        return {
            "deal_id": self.deal_id,
            "strategy": self.strategy,
            "rationale": self.rationale,
            "reasoning_steps": self.reasoning_steps,
            "information_needs": self.information_needs,
            "domain_knowledge": [chunk.model_dump() for chunk in self.domain_knowledge],
            "used_domain_chunks": self.used_domain_chunks,
            "decision_basis": self.decision_basis,
        }
