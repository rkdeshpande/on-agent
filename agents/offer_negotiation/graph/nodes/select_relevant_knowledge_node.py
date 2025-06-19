import json
import logging
from datetime import UTC, datetime
from typing import Callable

from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from agents.offer_negotiation.graph.state import AgentState
from agents.offer_negotiation.graph.utils import log_state
from agents.offer_negotiation.models.output_models import DomainKnowledgeItem
from agents.offer_negotiation.utils.model import get_llm
from agents.offer_negotiation.utils.prompt_loader import load_prompt
from agents.offer_negotiation.utils.trace_metadata import (
    add_error_metadata,
    add_performance_metadata,
    create_trace_metadata,
)

logger = logging.getLogger(__name__)


def create_select_relevant_knowledge_node() -> Callable:
    """Create a node that selects relevant domain knowledge for the specific deal."""

    # Get the LLM
    llm = get_llm()

    # Create the prompt template
    select_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", load_prompt("select_relevant_knowledge.md")),
            (
                "human",
                "Please analyze the deal context and select the most relevant domain knowledge chunks.",
            ),
        ]
    )

    @traceable(
        name="select_relevant_knowledge",
        run_type="chain",
    )
    def select_relevant_knowledge(state: AgentState) -> AgentState:
        """Select relevant domain knowledge based on deal context."""
        # Create trace metadata
        start_time = datetime.now(UTC)
        trace = create_trace_metadata("select_relevant_knowledge", state)

        try:
            logger.info("=== Starting select_relevant_knowledge node ===")
            log_state(state, "Input ")

            # Validate required fields
            if not state.context_summary:
                raise ValueError(
                    "Required field 'context_summary' missing from input state"
                )
            if not state.domain_knowledge:
                raise ValueError(
                    "Required field 'domain_knowledge' missing from input state"
                )

            # Format domain knowledge for the prompt
            domain_knowledge_text = "\n".join(
                [
                    f"Chunk {i + 1}:\n{chunk.text}\n(Source: {chunk.metadata.get('document_type', 'Unknown')})\n"
                    for i, chunk in enumerate(state.domain_knowledge)
                ]
            )

            # Generate relevant knowledge selection using LLM
            chain = select_prompt | llm
            response = chain.invoke(
                {
                    "deal_context": state.context_summary.model_dump(),
                    "domain_knowledge": domain_knowledge_text
                    or "No domain knowledge available.",
                }
            )

            # Parse the response into DomainKnowledgeItem list
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
                    # If response is an object, look for relevant_domain_knowledge key
                    relevant_items_data = parsed_data.get(
                        "relevant_domain_knowledge", []
                    )
                else:
                    # If response is an array, use it directly
                    relevant_items_data = parsed_data

                # Create DomainKnowledgeItem objects from parsed data
                relevant_knowledge = []
                for item_data in relevant_items_data:
                    if isinstance(item_data, dict):
                        # Create DomainKnowledgeItem from the parsed data
                        # Note: We'll need to map the chunk data to actual DocumentChunk objects
                        # For now, we'll use the first chunk as a placeholder
                        chunk = (
                            state.domain_knowledge[0]
                            if state.domain_knowledge
                            else None
                        )
                        relevant_knowledge.append(
                            DomainKnowledgeItem(
                                chunk=chunk,
                                relevance_reason=item_data.get("relevance_reason", ""),
                                application_context=item_data.get(
                                    "application_context", ""
                                ),
                            )
                        )

                logger.info(
                    f"Successfully parsed LLM response into {len(relevant_knowledge)} DomainKnowledgeItem objects"
                )

            except (json.JSONDecodeError, ValueError, TypeError, IndexError) as e:
                logger.warning(f"Failed to parse LLM response: {e}")
                logger.warning(f"Raw response: {response.content}")

                # Return empty list if parsing fails
                logger.info(
                    "Using empty relevant knowledge list due to parsing failure"
                )
                relevant_knowledge = []

            # Add performance metadata
            end_time = datetime.now(UTC)
            trace = add_performance_metadata(
                trace,
                start_time,
                end_time,
                {
                    "total_chunks_analyzed": len(state.domain_knowledge),
                    "relevant_chunks_selected": len(relevant_knowledge),
                    "relevant_knowledge_selected": True,
                    "parsing_successful": len(relevant_knowledge) > 0,
                },
            )

            logger.info("=== Completed select_relevant_knowledge node ===")
            log_state(state, "Output ")

            # Update state with relevant knowledge
            state.relevant_domain_knowledge = relevant_knowledge
            return state

        except Exception as e:
            logger.error(f"Error in select_relevant_knowledge: {str(e)}")
            trace = add_error_metadata(
                trace,
                str(e),
                {"state_keys": list(state.__dict__.keys()) if state else []},
            )
            raise

    return select_relevant_knowledge
