import json
import logging
from datetime import UTC, datetime
from typing import Callable

from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from agents.offer_negotiation.graph.state import AgentState
from agents.offer_negotiation.graph.utils import log_state
from agents.offer_negotiation.models.output_models import InformationGap
from agents.offer_negotiation.utils.model import get_llm
from agents.offer_negotiation.utils.prompt_loader import load_prompt
from agents.offer_negotiation.utils.trace_metadata import (
    add_error_metadata,
    add_performance_metadata,
    create_trace_metadata,
)

logger = logging.getLogger(__name__)


def create_identify_information_gaps_node() -> Callable:
    """Create a node that identifies information gaps critical for negotiation strategy."""

    # Get the LLM
    llm = get_llm()

    # Create the prompt template
    gaps_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", load_prompt("identify_information_gaps.md")),
            (
                "human",
                "Please analyze the available information and identify critical gaps that could impact negotiation strategy.",
            ),
        ]
    )

    @traceable(
        name="identify_information_gaps",
        run_type="chain",
    )
    def identify_information_gaps(state: AgentState) -> AgentState:
        """Identify information gaps that could impact negotiation strategy."""
        # Create trace metadata
        start_time = datetime.now(UTC)
        trace = create_trace_metadata("identify_information_gaps", state)

        try:
            logger.info("=== Starting identify_information_gaps node ===")
            log_state(state, "Input ")

            # Validate required fields
            if not state.context_summary:
                raise ValueError(
                    "Required field 'context_summary' missing from input state"
                )
            if not state.relevant_domain_knowledge:
                raise ValueError(
                    "Required field 'relevant_domain_knowledge' missing from input state"
                )

            # Generate information gaps analysis using LLM
            chain = gaps_prompt | llm
            response = chain.invoke(
                {
                    "context_summary": state.context_summary.model_dump(),
                    "relevant_domain_knowledge": [
                        {
                            "text": item.chunk.text,
                            "relevance_reason": item.relevance_reason,
                            "application_context": item.application_context,
                        }
                        for item in state.relevant_domain_knowledge
                    ],
                }
            )

            # Parse the response into InformationGap list
            try:
                # Extract JSON from the response
                response_text = response.content

                # Try to find JSON in the response (handle cases where LLM adds extra text)
                start_idx = response_text.find("[")
                end_idx = response_text.rfind("]") + 1

                if start_idx == -1 or end_idx == 0:
                    # Try to find JSON object instead
                    start_idx = response_text.find("{")
                    end_idx = response_text.rfind("}") + 1

                if start_idx == -1 or end_idx == 0:
                    raise ValueError("No JSON array or object found in LLM response")

                json_str = response_text[start_idx:end_idx]
                parsed_data = json.loads(json_str)

                # Handle both array and object responses
                if isinstance(parsed_data, dict):
                    # If response is an object, look for information_gaps key
                    gaps_data = parsed_data.get("information_gaps", [])
                else:
                    # If response is an array, use it directly
                    gaps_data = parsed_data

                # Create InformationGap objects from parsed data
                information_gaps = []
                for gap_data in gaps_data:
                    if isinstance(gap_data, dict):
                        information_gaps.append(
                            InformationGap(
                                gap_description=gap_data.get("gap_description", ""),
                                recommended_action=gap_data.get(
                                    "recommended_action", ""
                                ),
                                priority=gap_data.get("priority", 1),
                                impact_on_strategy=gap_data.get(
                                    "impact_on_strategy", ""
                                ),
                            )
                        )

                logger.info(
                    f"Successfully parsed LLM response into {len(information_gaps)} InformationGap objects"
                )

            except (json.JSONDecodeError, ValueError, TypeError) as e:
                logger.warning(f"Failed to parse LLM response: {e}")
                logger.warning(f"Raw response: {response.content}")

                # Return empty list if parsing fails
                logger.info("Using empty information gaps list due to parsing failure")
                information_gaps = []

            # Add performance metadata
            end_time = datetime.now(UTC)
            trace = add_performance_metadata(
                trace,
                start_time,
                end_time,
                {
                    "context_summary_analyzed": True,
                    "relevant_knowledge_items": len(state.relevant_domain_knowledge),
                    "information_gaps_identified": len(information_gaps),
                    "parsing_successful": len(information_gaps) > 0,
                },
            )

            logger.info("=== Completed identify_information_gaps node ===")
            log_state(state, "Output ")

            # Update state with information gaps
            state.information_gaps = information_gaps
            return state

        except Exception as e:
            logger.error(f"Error in identify_information_gaps: {str(e)}")
            trace = add_error_metadata(
                trace,
                str(e),
                {"state_keys": list(state.__dict__.keys()) if state else []},
            )
            raise

    return identify_information_gaps
