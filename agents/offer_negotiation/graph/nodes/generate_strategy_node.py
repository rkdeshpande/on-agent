import logging
from typing import Callable, Dict, List, Optional, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from agents.offer_negotiation.core.models.deal_models import DealContext
from agents.offer_negotiation.graph.state import DomainKnowledgeState, StrategyState
from agents.offer_negotiation.utils.model import get_llm

logger = logging.getLogger(__name__)


class DecisionBasis(TypedDict):
    heuristic: str
    justification: str
    confidence: str


def evaluate_heuristics(deal_context: DealContext) -> List[DecisionBasis]:
    """Evaluate deal context against defined heuristics and return matching decisions."""
    decisions: List[DecisionBasis] = []

    # Heuristic 1: Premium Objection → Deductible Trade
    if any(
        "premium" in obj.lower() for obj in deal_context.negotiation_context.objections
    ):
        # Check if client has history of accepting deductible adjustments
        has_deductible_history = any(
            "deductible" in note.lower()
            for note in deal_context.client_history.prior_negotiations
        )

        if has_deductible_history:
            decisions.append(
                {
                    "heuristic": "Premium Objection → Deductible Trade",
                    "justification": "Client objected to premium and has history of accepting deductible adjustments",
                    "confidence": "High - Matches objection pattern and client history",
                }
            )

    # Heuristic 2: Coverage Request → Evaluate Against Limits
    if any(
        "coverage" in obj.lower() for obj in deal_context.negotiation_context.objections
    ):
        # Extract current limits from coverage terms
        try:
            # Parse coverage terms to get current limits
            coverage_terms = deal_context.submission.coverage_terms.lower()
            if "limit" in coverage_terms:
                # limit_str = coverage_terms.split("$")[1].split()[0]
                # current_limit = float(limit_str.replace("m", "000000"))

                # Check for specific coverage requests in objections
                for objection in deal_context.negotiation_context.objections:
                    if "business interruption" in objection.lower():
                        decisions.append(
                            {
                                "heuristic": "Coverage Request → Business Interruption",
                                "justification": "Client requested additional business interruption coverage",
                                "confidence": "High - Explicit coverage request",
                            }
                        )
                    elif "flood" in objection.lower():
                        decisions.append(
                            {
                                "heuristic": "Coverage Request → Flood Coverage",
                                "justification": "Client requested flood coverage consideration",
                                "confidence": "High - Explicit coverage request",
                            }
                        )
        except (IndexError, ValueError):
            logger.warning("Could not parse coverage limits from terms")

    # Heuristic 3: Risk Profile → Coverage Adjustments
    if deal_context.submission.risk_profile:
        risk_profile = deal_context.submission.risk_profile.lower()
        if "high-risk" in risk_profile:
            decisions.append(
                {
                    "heuristic": "High Risk → Enhanced Coverage",
                    "justification": "High-risk profile suggests need for enhanced coverage options",
                    "confidence": "Medium - Based on risk profile",
                }
            )

    return decisions


def create_generate_strategy_node() -> Callable:
    """Create a node that generates a negotiation strategy based on deal context and domain knowledge."""

    # Get the LLM
    llm = get_llm()

    # Create the prompt template
    strategy_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert insurance negotiator. Your task is to generate a negotiation strategy based on the deal context, domain knowledge, and identified decision rules.

Deal Context:
{deal_context}

Domain Knowledge:
{domain_knowledge}

Decision Rules Applied:
{decision_rules}

Generate a detailed negotiation strategy that:
1. Addresses the client's objections
2. Leverages the client's history
3. Uses insights from comparable deals
4. Considers the risk profile
5. Provides specific recommendations for premium and deductible adjustments
6. Handles coverage requests appropriately

Your strategy should explicitly incorporate the decision rules that were triggered. For example:
- If a premium objection rule was triggered, explain how you're using deductible adjustments
- If a coverage request rule was triggered, explain how you're addressing the coverage needs
- If a high-risk rule was triggered, explain how you're adjusting coverage for risk mitigation

For coverage requests:
- Evaluate if the request is reasonable given the risk profile
- Consider if additional coverage can be offered within existing limits
- Suggest alternative coverage options if direct request cannot be accommodated
- Explain any coverage limitations or exclusions clearly

Format your response as a structured strategy with clear sections.

Here is an example of how to respond to a premium objection scenario:

Example:
Deal Context:
{
  "submission": {
    "deal_id": "EXAMPLE123",
    "coverage_terms": "Commercial Property: $8M limit, $75K deductible",
    "risk_profile": "Medium-risk retail facility",
    "premium_structure": "Annual premium: $180K, Quarterly payments",
    "line_of_business": "Commercial Property",
    "territory": "Southeast"
  },
  "client_history": {
    "client_id": "CLIENT789",
    "prior_negotiations": ["2022 Renewal: Negotiated 10% premium reduction"],
    "relationship_notes": "Client since 2020, good payment history",
    "claim_summary": "No major claims"
  },
  "negotiation_context": {
    "deal_id": "EXAMPLE123",
    "discussion_notes": ["Initial meeting: Client concerned about premium"],
    "offers": ["Initial offer: $180K premium, $75K deductible"],
    "objections": ["Premium too high compared to market"]
  },
  "comparable_deals": [
    {
      "reference_deal_id": "DEAL456",
      "similarity_reason": "Similar retail facility",
      "outcome_summary": "Negotiated to $160K premium with $100K deductible"
    }
  ]
}

Domain Knowledge:
- Premium adjustments may be considered for clients with good payment history and no major claims.
- Deductible adjustments can be used to offset premium increases.

Decision Rules Applied:
- Premium Objection Rule: Consider deductible adjustments to offset premium concerns.

Strategy:
1. Acknowledge the client's concern about the premium being too high compared to market rates.
2. Leverage the client's good payment history and no major claims to justify a premium reduction.
3. Reference the comparable deal DEAL456, which negotiated a $160K premium with a $100K deductible.
4. Propose a revised offer: $170K premium with a $90K deductible, balancing the client's premium objection with risk management.
5. Explain that the deductible adjustment helps offset the premium cost while maintaining appropriate risk coverage.

Rationale:
- The premium reduction is justified by the client's good payment history and no major claims.
- The deductible adjustment is a tradeoff to address the premium objection while maintaining risk coverage.
- The comparable deal provides a benchmark for the proposed premium and deductible adjustments.
""",
            ),
            (
                "human",
                "Please generate a negotiation strategy based on the provided context and decision rules.",
            ),
        ]
    )

    @traceable(name="generate_strategy", run_type="chain")
    def generate_strategy(state: DomainKnowledgeState) -> StrategyState:
        logger.info("=== Starting generate_strategy node ===")
        logger.debug(f"Input state: {state}")

        # Extract deal context
        deal_context = DealContext(**state["deal_context"])

        # Evaluate heuristics
        decisions = evaluate_heuristics(deal_context)

        # Log triggered heuristics
        for decision in decisions:
            logger.info(
                f"Triggered heuristic: {decision['heuristic']}\n"
                f"Justification: {decision['justification']}\n"
                f"Confidence: {decision['confidence']}"
            )

        # Format domain knowledge
        domain_knowledge = "\n".join(
            [
                f"- {chunk['text']} (Source: {chunk['metadata']['document_type']})"
                for chunk in state["domain_chunks"]
            ]
        )

        # Format decision rules for prompt
        decision_rules = (
            "\n".join(
                [
                    f"- {decision['heuristic']}: {decision['justification']}"
                    for decision in decisions
                ]
            )
            or "No specific decision rules were triggered."
        )

        # Generate strategy using LLM
        chain = strategy_prompt | llm
        response = chain.invoke(
            {
                "deal_context": deal_context.model_dump_json(indent=2),
                "domain_knowledge": domain_knowledge
                or "No specific domain knowledge available.",
                "decision_rules": decision_rules,
            }
        )

        strategy = response.content
        logger.info(f"Generated strategy: {strategy}")

        # Update state with strategy and decision basis
        updated_state: StrategyState = {
            **state,
            "strategy": strategy,
            "decision_basis": [decision for decision in decisions],
        }

        logger.info("=== Completed generate_strategy node ===")
        logger.debug(f"Output state: {updated_state}")

        return updated_state

    return generate_strategy
