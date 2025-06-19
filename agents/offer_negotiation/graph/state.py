from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from agents.offer_negotiation.core.models.deal_models import DealContext
from agents.offer_negotiation.knowledge.domain_documents import DocumentChunk
from agents.offer_negotiation.models.output_models import (
    ContextSummary,
    DomainKnowledgeItem,
    InformationGap,
)


class AgentState(BaseModel):
    """Single state class for the entire agent workflow."""

    # Basic fields
    deal_id: str
    error: Optional[str] = None

    # Deal context
    deal_context: Optional[Dict[str, Any]] = None

    # Information needs
    information_needs: List[str] = Field(default_factory=list)
    information_gaps: List[InformationGap] = Field(default_factory=list)

    # Domain knowledge
    domain_knowledge: List[DocumentChunk] = Field(default_factory=list)
    used_domain_chunks: List[Dict[str, str]] = Field(default_factory=list)
    relevant_domain_knowledge: List[DomainKnowledgeItem] = Field(default_factory=list)

    # Strategy
    strategy: Optional[str] = None
    used_deal_fields: Set[str] = Field(default_factory=set)
    decision_basis: List[Dict[str, str]] = Field(default_factory=list)

    # Rationale
    rationale: Optional[str] = None
    reasoning_steps: List[str] = Field(default_factory=list)
    reasoning_output: Dict[str, Any] = Field(default_factory=dict)

    # Structured output
    context_summary: Optional[ContextSummary] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to a dictionary for output."""
        result = {
            "deal_id": self.deal_id,
            "strategy": self.strategy,
            "rationale": self.rationale,
            "reasoning_steps": self.reasoning_steps,
            "information_needs": self.information_needs,
            "domain_knowledge": [chunk.model_dump() for chunk in self.domain_knowledge],
            "used_domain_chunks": self.used_domain_chunks,
            "decision_basis": self.decision_basis,
        }
        if self.context_summary is not None:
            result["context_summary"] = self.context_summary.model_dump()
        if self.relevant_domain_knowledge:
            result["relevant_domain_knowledge"] = [
                item.model_dump() for item in self.relevant_domain_knowledge
            ]
        if self.information_gaps:
            result["information_gaps"] = [
                gap.model_dump() for gap in self.information_gaps
            ]
        return result
