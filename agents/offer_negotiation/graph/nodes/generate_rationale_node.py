import json
import logging
import re
from datetime import UTC, datetime
from typing import Callable

from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from agents.offer_negotiation.graph.state import AgentState
from agents.offer_negotiation.graph.utils import log_state
from agents.offer_negotiation.models.output_models import StrategyRationale
from agents.offer_negotiation.utils.model import get_llm
from agents.offer_negotiation.utils.prompt_loader import load_prompt
from agents.offer_negotiation.utils.trace_metadata import (
    add_error_metadata,
    add_performance_metadata,
    create_trace_metadata,
)

logger = logging.getLogger(__name__)


def create_generate_rationale_node() -> Callable:
    """
    Create a node that generates detailed rationale for each negotiation strategy.

    This node analyzes the strategies and context to provide comprehensive
    explanations for why each strategy approach was chosen and how it
    addresses the specific deal context.
    """

    # Get the LLM instance for rationale generation
    llm = get_llm()

    # Create the prompt template for rationale generation
    rationale_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", load_prompt("rationale_explanation.md")),
            (
                "human",
                "Please analyze the provided context and strategies to generate detailed rationale for each approach.",
            ),
        ]
    )

    @traceable(
        name="generate_rationale",
        run_type="chain",
    )
    def generate_rationale(state: AgentState) -> AgentState:
        """
        Generate detailed rationale for each negotiation strategy based on the complete context.

        This function:
        1. Validates that all required context and strategies are available
        2. Formats the context for the LLM prompt
        3. Calls the LLM to generate rationale
        4. Parses and validates the response
        5. Updates the state with the generated rationale
        """
        print("=== GENERATE_RATIONALE NODE STARTED ===")

        # Create trace metadata for performance tracking
        start_time = datetime.now(UTC)
        trace = create_trace_metadata("generate_rationale", state)

        try:
            logger.info("=== Starting generate_rationale node ===")
            log_state(state, "Input ")

            # STEP 1: Validate that all required context is available
            logger.info("Validating required context fields...")
            if not state.context_summary:
                raise ValueError(
                    "Required field 'context_summary' missing from input state"
                )
            if not state.strategy:
                raise ValueError("Required field 'strategy' missing from input state")
            if not state.relevant_domain_knowledge:
                logger.warning(
                    "No relevant domain knowledge available - rationale may be less informed"
                )

            # STEP 2: Format the context for the LLM prompt
            logger.info("Formatting context for LLM prompt...")

            # Format deal context for the prompt
            deal_context_text = f"""
Deal Summary:
- Coverage Terms: {state.context_summary.deal_summary.coverage_terms}
- Risk Profile: {state.context_summary.deal_summary.risk_profile}
- Premium Structure: {state.context_summary.deal_summary.premium_structure}
- Line of Business: {state.context_summary.deal_summary.line_of_business}
- Territory: {state.context_summary.deal_summary.territory}
- Key Risk Factors: {', '.join(state.context_summary.deal_summary.key_risk_factors)}
- Current Offer Details: {state.context_summary.deal_summary.current_offer_details}

Client Summary:
- Relationship Duration: {state.context_summary.client_summary.relationship_duration}
- Negotiation Style: {state.context_summary.client_summary.negotiation_style}
- Claim History: {state.context_summary.client_summary.claim_history}
- Payment History: {state.context_summary.client_summary.payment_history}
- Prior Negotiation History: {', '.join(state.context_summary.client_summary.prior_negotiation_history)}

Negotiation Context:
- Current Objections: {', '.join(state.context_summary.negotiation_context.current_objections)}
- Client Priorities: {', '.join(state.context_summary.negotiation_context.client_priorities)}
- Discussion Progress: {', '.join(state.context_summary.negotiation_context.discussion_progress)}
"""

            # Format strategies for the prompt
            strategy_text = f"""
Generated Strategies:

Conservative Strategy:
{json.dumps([rec.model_dump() for rec in state.strategy.conservative], indent=2)}

Moderate Strategy:
{json.dumps([rec.model_dump() for rec in state.strategy.moderate], indent=2)}

Aggressive Strategy:
{json.dumps([rec.model_dump() for rec in state.strategy.aggressive], indent=2)}
"""

            # Format relevant domain knowledge for the prompt
            domain_knowledge_text = (
                "\n".join(
                    [
                        f"- {item.chunk.text} (Relevance: {item.relevance_reason})"
                        for item in state.relevant_domain_knowledge
                    ]
                )
                if state.relevant_domain_knowledge
                else "No relevant domain knowledge available."
            )

            # STEP 3: Call the LLM to generate rationale
            logger.info("Calling LLM to generate rationale...")
            chain = rationale_prompt | llm

            print("=== BEFORE LLM CALL (generate_rationale) ===")
            response = chain.invoke(
                {
                    "deal_context": deal_context_text,
                    "strategy": strategy_text,
                    "domain_knowledge": domain_knowledge_text,
                }
            )
            print("=== AFTER LLM CALL (generate_rationale) ===")

            # STEP 4: Log the raw LLM response for debugging
            response_text = getattr(response, "content", None)
            print(
                f"\n===== RAW LLM RESPONSE (generate_rationale_node) =====\n{str(response_text)[:2000]}...\n===============================================\n"
            )
            logger.info(
                f"Raw LLM response length: {len(str(response_text))} characters"
            )

            # STEP 5: Parse the response into StrategyRationale
            try:
                # Extract JSON from the response
                logger.info(f"Raw LLM response length: {len(response_text)} characters")

                # Try to find JSON in the response (handle cases where LLM adds extra text)
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1

                if start_idx == -1 or end_idx == 0:
                    raise ValueError("No JSON object found in LLM response")

                json_str = response_text[start_idx:end_idx]
                logger.info(f"Extracted JSON string length: {len(json_str)} characters")

                # Try to fix common JSON issues
                # 1. Remove any trailing incomplete objects
                brace_count = 0
                last_complete_pos = 0
                for i, char in enumerate(json_str):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            last_complete_pos = i + 1

                if last_complete_pos > 0:
                    json_str = json_str[:last_complete_pos]
                    logger.info(f"Fixed JSON string length: {len(json_str)} characters")

                # 2. Try to complete any incomplete objects
                if json_str.count("{") > json_str.count("}"):
                    # Add missing closing braces
                    missing_braces = json_str.count("{") - json_str.count("}")
                    json_str += "}" * missing_braces
                    logger.info(f"Added {missing_braces} missing closing braces")

                # Parse the JSON
                rationale_data = json.loads(json_str)
                logger.info("Successfully parsed JSON response")

                # Convert to StrategyRationale model
                rationale = StrategyRationale(**rationale_data)
                logger.info("Successfully created StrategyRationale object")

            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse LLM response: {e}")
                logger.error(f"Raw response: {response_text}")

                # Create a fallback rationale with the raw response
                rationale = StrategyRationale(
                    conservative_rationale="Failed to parse rationale from LLM response",
                    moderate_rationale="Failed to parse rationale from LLM response",
                    aggressive_rationale="Failed to parse rationale from LLM response",
                    decision_factors=["Error in rationale generation"],
                    client_history_impact="Unable to determine impact due to parsing error",
                    comparable_deals_impact="Unable to determine impact due to parsing error",
                    risk_profile_considerations="Unable to determine considerations due to parsing error",
                )

                # Add error metadata
                add_error_metadata(trace, "json_parsing_error", str(e), response_text)

            # STEP 6: Update the state with the generated rationale
            logger.info("Updating state with generated rationale...")
            state.rationale = rationale

            # STEP 7: Log the final state
            logger.info("=== Final state after generate_rationale ===")
            log_state(state, "Output ")

            # Add performance metadata
            end_time = datetime.now(UTC)
            add_performance_metadata(trace, start_time, end_time)

            print("=== GENERATE_RATIONALE NODE COMPLETED ===")
            return state

        except Exception as e:
            logger.error(f"Error in generate_rationale node: {e}")

            # Create a fallback rationale
            state.rationale = StrategyRationale(
                conservative_rationale=f"Error generating rationale: {str(e)}",
                moderate_rationale=f"Error generating rationale: {str(e)}",
                aggressive_rationale=f"Error generating rationale: {str(e)}",
                decision_factors=["Error in rationale generation"],
                client_history_impact="Unable to determine impact due to error",
                comparable_deals_impact="Unable to determine impact due to error",
                risk_profile_considerations="Unable to determine considerations due to error",
            )

            # Add error metadata
            add_error_metadata(trace, e)

            print("=== GENERATE_RATIONALE NODE FAILED ===")
            return state

    return generate_rationale
