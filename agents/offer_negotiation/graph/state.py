from typing import Dict, List, Optional, Set, TypedDict

from agents.offer_negotiation.core.models.deal_models import DealContext
from agents.offer_negotiation.knowledge.domain_documents import DocumentChunk


class BaseState(TypedDict):
    """Base state shared across all nodes."""

    deal_id: str
    error: Optional[str]  # For error tracking


class DealContextState(BaseState):
    """State for deal context node."""

    deal_context: Optional[Dict]  # Will be populated with DealContext data


class InformationNeedsState(DealContextState):
    """State for information needs node."""

    information_needs: List[str]  # List of fields we need to focus on


class DomainKnowledgeState(InformationNeedsState):
    """State for domain knowledge node."""

    domain_chunks: List[Dict]  # List of relevant DocumentChunks
    used_domain_chunks: List[Dict[str, str]]  # Which chunks were used and why


class StrategyState(DomainKnowledgeState):
    """State for strategy generation node."""

    strategy: str  # The generated strategy
    used_deal_fields: Set[str]  # Which deal fields were used


class FinalState(StrategyState):
    """Final state with complete reasoning output."""

    rationale: str  # Explanation of the strategy
    reasoning_steps: List[str]  # Step-by-step reasoning process
