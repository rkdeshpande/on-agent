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

================ FEW-SHOT EXAMPLES ================

=== EXAMPLE 1: PREMIUM OBJECTION SCENARIO ===

Deal Context Summary:
- Deal ID: EXAMPLE123
- Line of Business: Commercial Property
- Risk Profile: Medium-risk retail facility
- Current Terms: $8M limit, $75K deductible
- Premium: $180K annually (Quarterly payments)

Key Objections:
1. Premium too high compared to market rates
2. Concern about quarterly payment structure

Domain Rules Used:
1. Premium Objection → Deductible Trade
   - Justification: Client has history of accepting deductible adjustments
   - Confidence: High - Matches objection pattern and client history

2. Payment Structure → Flexible Terms
   - Justification: Client has good payment history
   - Confidence: High - Based on relationship notes

Strategy:
1. Premium Adjustment
   - Current: $180K annually
   - Proposed: $170K annually
   - Justification:
     * Client's good payment history
     * No major claims
     * Comparable deal benchmark (DEAL456)

2. Deductible Trade-off
   - Current: $75K
   - Proposed: $90K
   - Justification:
     * Offsets premium reduction
     * Maintains risk coverage
     * Aligns with client's deductible acceptance history

3. Payment Structure
   - Current: Quarterly payments
   - Proposed: Monthly payments with 2% discount for annual payment
   - Justification:
     * Provides flexibility
     * Rewards annual commitment
     * Based on client's payment history

Rationale:
1. Premium Reduction
   - Supported by client's clean claims history
   - Validated by comparable deal (DEAL456)
   - Within acceptable risk parameters

2. Deductible Increase
   - Balanced trade-off for premium reduction
   - Client has demonstrated acceptance of similar adjustments
   - Maintains appropriate risk coverage

3. Payment Flexibility
   - Addresses cash flow concerns
   - Rewards long-term commitment
   - Based on client's payment history

Expected Outcome:
- Premium reduction addresses market comparison concern
- Deductible adjustment maintains risk coverage
- Flexible payment options improve client satisfaction
- Strategy leverages client history and comparable deals

=== END EXAMPLE 1 ===

=== EXAMPLE 2: COVERAGE REQUEST SCENARIO ===
Deal Context Summary:
- Deal ID: COVREQ001
- Line of Business: Commercial Property
- Risk Profile: Low-risk office park
- Current Terms: $12M limit, $100K deductible
- Premium: $200K annually

Key Objections:
1. Request for flood coverage
2. Request for higher business interruption limit

Domain Rules Used:
1. Coverage Request → Evaluate Against Limits
   - Justification: Client requested additional coverage types
   - Confidence: High - Explicit coverage request

2. Coverage Cap → Exclusion/Alternative
   - Justification: Requested coverage exceeds domain limits
   - Confidence: High - Based on policy guidelines

Strategy:
1. Flood Coverage
   - Current: Not included
   - Proposed: Offer sublimit of $1M for flood, subject to underwriting
   - Justification:
     * Flood risk is moderate in this territory
     * Comparable deal (COVDEAL002) included $1M flood sublimit

2. Business Interruption Limit
   - Current: $2M
   - Proposed: $2.5M (max allowed by guidelines)
   - Justification:
     * Requested $3M exceeds domain cap
     * $2.5M is the highest available for this risk profile
     * Explain cap and rationale to client

Rationale:
- Flood coverage is offered within prudent risk management
- Business interruption limit is maximized per guidelines
- Transparent communication about exclusions and caps

Expected Outcome:
- Client receives additional coverage within risk and policy limits
- Clear rationale for any exclusions or caps
- Strategy leverages comparable deals and domain knowledge
=== END EXAMPLE 2 ===

=== EXAMPLE 3: HIGH-RISK SCENARIO ===
Deal Context Summary:
- Deal ID: HIGHRISK01
- Line of Business: Manufacturing
- Risk Profile: High-risk chemical plant
- Current Terms: $20M limit, $500K deductible
- Premium: $1.2M annually

Key Objections:
1. Premium is too high
2. Deductible is too high

Domain Rules Used:
1. High Risk → Enhanced Coverage/Strict Terms
   - Justification: High-risk profile requires stricter terms
   - Confidence: Medium - Based on risk assessment

2. Premium Objection → Deductible Trade (limited)
   - Justification: Some flexibility, but must maintain risk controls
   - Confidence: Low - Limited by risk profile

Strategy:
1. Premium Adjustment
   - Current: $1.2M
   - Proposed: $1.15M (minimum for this risk)
   - Justification:
     * High-risk profile limits premium reduction
     * Comparable deal (HRDEAL03) had $1.18M premium

2. Deductible Adjustment
   - Current: $500K
   - Proposed: $450K (minimum allowed)
   - Justification:
     * Some flexibility for client
     * Must maintain risk controls
     * Explain rationale and limits

3. Enhanced Safety Requirements
   - Proposed: Require additional safety audits and compliance
   - Justification:
     * Mitigates risk for both parties
     * May allow for future premium/deductible improvements

Rationale:
- High-risk profile constrains flexibility
- Adjustments are made within strict risk and policy limits
- Safety improvements are required for future concessions

Expected Outcome:
- Client receives modest premium/deductible relief
- Safety requirements are clearly communicated
- Strategy is justified by risk profile, comparable deals, and domain knowledge
=== END EXAMPLE 3 ===

================ END FEW-SHOT EXAMPLES ================

Now, please generate a negotiation strategy for the current deal context following this structured format.""",
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
