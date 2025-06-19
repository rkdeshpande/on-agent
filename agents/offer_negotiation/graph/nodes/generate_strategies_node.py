import json
import logging
import re
from datetime import UTC, datetime
from typing import Callable

from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from agents.offer_negotiation.graph.state import AgentState
from agents.offer_negotiation.graph.utils import log_state
from agents.offer_negotiation.models.output_models import NegotiationStrategy
from agents.offer_negotiation.utils.model import get_llm
from agents.offer_negotiation.utils.prompt_loader import load_prompt
from agents.offer_negotiation.utils.trace_metadata import (
    add_error_metadata,
    add_performance_metadata,
    create_trace_metadata,
)

logger = logging.getLogger(__name__)


def create_generate_strategies_node() -> Callable:
    """
    Create a node that generates three distinct negotiation strategies:
    Conservative, Moderate, and Aggressive.

    This node analyzes the complete context (deal, client, domain knowledge,
    information gaps) and creates actionable strategies with specific recommendations
    for each approach.
    """

    # Get the LLM instance for strategy generation
    llm = get_llm()

    # Create the prompt template for strategy generation
    # This prompt will guide the LLM to create three distinct strategies
    strategies_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", load_prompt("generate_strategies.md")),
            (
                "human",
                "Please analyze the provided context and generate three distinct negotiation strategies.",
            ),
        ]
    )

    @traceable(
        name="generate_strategies",
        run_type="chain",
    )
    def generate_strategies(state: AgentState) -> AgentState:
        """
        Generate three distinct negotiation strategies based on the complete context.

        This function:
        1. Validates that all required context is available
        2. Formats the context for the LLM prompt
        3. Calls the LLM to generate strategies
        4. Parses and validates the response
        5. Updates the state with the generated strategies
        """
        print("=== GENERATE_STRATEGIES NODE STARTED ===")

        # Create trace metadata for performance tracking
        start_time = datetime.now(UTC)
        trace = create_trace_metadata("generate_strategies", state)

        try:
            logger.info("=== Starting generate_strategies node ===")
            log_state(state, "Input ")

            # STEP 1: Validate that all required context is available
            logger.info("Validating required context fields...")
            if not state.context_summary:
                raise ValueError(
                    "Required field 'context_summary' missing from input state"
                )
            if not state.relevant_domain_knowledge:
                logger.warning(
                    "No relevant domain knowledge available - strategies may be less informed"
                )
            if not state.information_gaps:
                logger.warning(
                    "No information gaps identified - strategies may not address data limitations"
                )

            # STEP 2: Format the context for the LLM prompt
            logger.info("Formatting context for LLM prompt...")

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

            # Format information gaps for the prompt
            information_gaps_text = (
                "\n".join(
                    [
                        f"- {gap.gap_description} (Priority: {gap.priority}, Action: {gap.recommended_action})"
                        for gap in state.information_gaps
                    ]
                )
                if state.information_gaps
                else "No information gaps identified."
            )

            # STEP 3: Call the LLM to generate strategies
            logger.info("Calling LLM to generate strategies...")
            chain = strategies_prompt | llm

            print("=== BEFORE LLM CALL (generate_strategies) ===")
            response = chain.invoke(
                {
                    "context_summary": state.context_summary.model_dump(),
                    "domain_knowledge": domain_knowledge_text,
                    "information_gaps": information_gaps_text,
                }
            )
            print("=== AFTER LLM CALL (generate_strategies) ===")

            # STEP 4: Log the raw LLM response for debugging
            response_text = getattr(response, "content", None)
            print(
                f"\n===== RAW LLM RESPONSE (generate_strategies_node) =====\n{str(response_text)[:2000]}...\n===============================================\n"
            )
            logger.info(
                f"Raw LLM response length: {len(str(response_text))} characters"
            )

            # STEP 5: Parse the response into NegotiationStrategy
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
                strategy_data = json.loads(json_str)
                logger.info("Successfully parsed JSON response")

                # Convert to NegotiationStrategy model
                strategy = NegotiationStrategy(**strategy_data)
                logger.info("Successfully created NegotiationStrategy object")

            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse LLM response: {e}")
                logger.error(f"Raw response: {response_text}")

                # Try to extract partial strategies if possible
                try:
                    # Look for individual strategy sections
                    conservative_match = re.search(
                        r'"conservative":\s*\[(.*?)\]', response_text, re.DOTALL
                    )
                    moderate_match = re.search(
                        r'"moderate":\s*\[(.*?)\]', response_text, re.DOTALL
                    )
                    aggressive_match = re.search(
                        r'"aggressive":\s*\[(.*?)\]', response_text, re.DOTALL
                    )

                    partial_strategies = {}
                    if conservative_match:
                        partial_strategies["conservative"] = []
                    if moderate_match:
                        partial_strategies["moderate"] = []
                    if aggressive_match:
                        partial_strategies["aggressive"] = []

                    if partial_strategies:
                        logger.info(
                            "Created partial strategy with empty arrays due to parsing failure"
                        )
                        strategy = NegotiationStrategy(**partial_strategies)
                    else:
                        logger.info(
                            "Using empty NegotiationStrategy due to parsing failure"
                        )
                        strategy = NegotiationStrategy()

                except Exception as recovery_error:
                    logger.error(f"Recovery attempt also failed: {recovery_error}")
                    logger.info(
                        "Using empty NegotiationStrategy due to parsing failure"
                    )
                    strategy = NegotiationStrategy()

            # STEP 6: Add performance metadata
            end_time = datetime.now(UTC)
            trace = add_performance_metadata(
                trace,
                start_time,
                end_time,
                {
                    "strategies_generated": True,
                    "conservative_recommendations": len(strategy.conservative),
                    "moderate_recommendations": len(strategy.moderate),
                    "aggressive_recommendations": len(strategy.aggressive),
                    "parsing_successful": hasattr(strategy, "conservative"),
                },
            )

            logger.info("=== Completed generate_strategies node ===")
            log_state(state, "Output ")

            # STEP 7: Update state with the generated strategies
            state.strategy = strategy
            return state

        except Exception as e:
            logger.error(f"Error in generate_strategies: {str(e)}")
            trace = add_error_metadata(
                trace,
                str(e),
                {"state_keys": list(state.__dict__.keys()) if state else []},
            )
            raise

    return generate_strategies
