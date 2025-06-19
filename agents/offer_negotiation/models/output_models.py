from typing import List, Optional

from pydantic import BaseModel, Field

from agents.offer_negotiation.knowledge.domain_documents import DocumentChunk


class DomainKnowledgeItem(BaseModel):
    """A relevant piece of domain knowledge with context."""

    chunk: DocumentChunk
    relevance_reason: str
    application_context: str


class DealSummary(BaseModel):
    """Structured summary of the deal context."""

    coverage_terms: str
    risk_profile: str
    premium_structure: str
    line_of_business: str
    territory: str
    key_risk_factors: List[str] = Field(default_factory=list)
    current_offer_details: str


class ClientSummary(BaseModel):
    """Structured summary of the client context."""

    relationship_duration: str
    prior_negotiation_history: List[str] = Field(default_factory=list)
    claim_history: str
    payment_history: str
    negotiation_style: str  # Based on prior interactions


class NegotiationContext(BaseModel):
    """Current state of the negotiation."""

    current_objections: List[str] = Field(default_factory=list)
    discussion_progress: List[str] = Field(default_factory=list)
    offer_history: List[str] = Field(default_factory=list)
    client_priorities: List[str] = Field(
        default_factory=list
    )  # Inferred from objections/discussions


class ComparableDeal(BaseModel):
    """A comparable deal for benchmarking."""

    reference_deal_id: str
    similarity_reason: str
    outcome_summary: str
    key_learnings: List[str] = Field(default_factory=list)


class ComparableDealsSummary(BaseModel):
    """Summary of comparable deals and market insights."""

    similar_deals: List[ComparableDeal] = Field(default_factory=list)
    market_trends: str
    benchmark_insights: str


class ContextSummary(BaseModel):
    """Comprehensive analysis of all available context."""

    deal_summary: DealSummary
    client_summary: ClientSummary
    negotiation_context: NegotiationContext
    comparable_deals: ComparableDealsSummary
    relevant_domain_knowledge: List[DomainKnowledgeItem] = Field(default_factory=list)
    key_insights: List[str] = Field(
        default_factory=list
    )  # Synthesized insights from all context


class StrategyRecommendation(BaseModel):
    """A specific recommendation within a strategy."""

    recommendation: str
    rationale: str  # Connection back to context
    impact: str
    confidence_level: str  # High/Medium/Low
    risk_level: str  # High/Medium/Low


class NegotiationStrategy(BaseModel):
    """A complete negotiation strategy with multiple recommendations."""

    conservative: List[StrategyRecommendation] = Field(default_factory=list)
    moderate: List[StrategyRecommendation] = Field(default_factory=list)
    aggressive: List[StrategyRecommendation] = Field(default_factory=list)


class InformationGap(BaseModel):
    """A gap in the available information with recommended action."""

    gap_description: str
    recommended_action: str
    priority: int  # 1 = highest priority
    impact_on_strategy: str  # How this gap affects our ability to create good strategies


class StrategyRationale(BaseModel):
    """Detailed rationale for each strategy level."""

    conservative_rationale: str
    moderate_rationale: str
    aggressive_rationale: str
    decision_factors: List[str] = Field(default_factory=list)
    client_history_impact: str
    comparable_deals_impact: str
    risk_profile_considerations: str


class AgentOutput(BaseModel):
    """Complete structured output from the negotiation agent."""

    context_summary: ContextSummary
    strategies: NegotiationStrategy
    information_gaps: List[InformationGap] = Field(default_factory=list)
    rationale: StrategyRationale
    overall_confidence: str  # High/Medium/Low
    next_steps: List[str] = Field(default_factory=list)
