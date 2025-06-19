import json
import logging
from datetime import UTC, datetime
from typing import Callable

from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from agents.offer_negotiation.graph.state import AgentState
from agents.offer_negotiation.graph.utils import log_state
from agents.offer_negotiation.models.output_models import ContextSummary
from agents.offer_negotiation.utils.model import get_llm
from agents.offer_negotiation.utils.prompt_loader import load_prompt
from agents.offer_negotiation.utils.trace_metadata import (
    add_error_metadata,
    add_performance_metadata,
    create_trace_metadata,
)

logger = logging.getLogger(__name__)


def create_analyze_context_node() -> Callable:
    """Create a node that analyzes deal context and creates a comprehensive ContextSummary."""

    # Get the LLM
    llm = get_llm()

    # Create the prompt template
    analyze_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", load_prompt("analyze_context.md")),
            (
                "human",
                "Please analyze the provided deal context and domain knowledge to create a comprehensive context summary.",
            ),
        ]
    )

    @traceable(
        name="analyze_context",
        run_type="chain",
    )
    def analyze_context(state: AgentState) -> AgentState:
        """Analyze deal context and create comprehensive ContextSummary."""
        print("=== ANALYZE_CONTEXT NODE STARTED ===")

        # Create trace metadata
        start_time = datetime.now(UTC)
        trace = create_trace_metadata("analyze_context", state)

        try:
            logger.info("=== Starting analyze_context node ===")
            log_state(state, "Input ")

            # Validate required fields
            if not state.deal_context:
                raise ValueError(
                    "Required field 'deal_context' missing from input state"
                )
            if not state.domain_knowledge:
                raise ValueError(
                    "Required field 'domain_knowledge' missing from input state"
                )

            # Format domain knowledge for the prompt
            domain_knowledge_text = "\n".join(
                [
                    f"- {chunk.text} (Source: {chunk.metadata.get('document_type', 'Unknown')})"
                    for chunk in state.domain_knowledge
                ]
            )

            # Generate context summary using LLM with structured output
            chain = analyze_prompt | llm
            print("=== BEFORE LLM CALL ===")
            response = chain.invoke(
                {
                    "deal_context": state.deal_context,
                    "domain_knowledge": domain_knowledge_text
                    or "No domain knowledge available.",
                }
            )
            print("=== AFTER LLM CALL ===")
            print("Response object:", repr(response))
            print("Response type:", type(response))
            print("Response content:", getattr(response, "content", None))

            # Print the raw LLM response immediately for debugging
            response_text = getattr(response, "content", None)
            print(
                "\n===== RAW LLM RESPONSE (analyze_context_node) =====\n"
                + str(response_text)[:1000]
                + "\n===============================================\n"
            )

            # Parse the response into ContextSummary
            try:
                # Extract JSON from the response
                logger.info(
                    f"Raw LLM response: {response_text[:500]}..."
                )  # Log first 500 chars

                # Try to find JSON in the response (handle cases where LLM adds extra text)
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1

                if start_idx == -1 or end_idx == 0:
                    raise ValueError("No JSON object found in LLM response")

                json_str = response_text[start_idx:end_idx]
                logger.info(
                    f"Extracted JSON string: {json_str[:500]}..."
                )  # Log first 500 chars

                parsed_data = json.loads(json_str)
                logger.info(
                    f"Successfully parsed JSON with keys: {list(parsed_data.keys())}"
                )

                # Handle relevant_domain_knowledge mapping from chunk_id to DocumentChunk objects
                if "relevant_domain_knowledge" in parsed_data:
                    relevant_knowledge_items = []
                    for item_data in parsed_data["relevant_domain_knowledge"]:
                        if isinstance(item_data, dict) and "chunk_id" in item_data:
                            # Find the corresponding DocumentChunk by chunk_id
                            chunk_id = item_data["chunk_id"]
                            matching_chunk = None
                            for chunk in state.domain_knowledge:
                                if chunk.chunk_id == chunk_id:
                                    matching_chunk = chunk
                                    break

                            if matching_chunk:
                                # Create DomainKnowledgeItem with the actual DocumentChunk
                                from agents.offer_negotiation.models.output_models import (
                                    DomainKnowledgeItem,
                                )

                                relevant_knowledge_items.append(
                                    DomainKnowledgeItem(
                                        chunk=matching_chunk,
                                        relevance_reason=item_data.get(
                                            "relevance_reason", ""
                                        ),
                                        application_context=item_data.get(
                                            "application_context", ""
                                        ),
                                    )
                                )
                            else:
                                logger.warning(
                                    f"Could not find chunk with ID: {chunk_id}"
                                )

                    # Replace the parsed data with the properly constructed DomainKnowledgeItem objects
                    parsed_data["relevant_domain_knowledge"] = relevant_knowledge_items

                # Create ContextSummary from parsed data
                context_summary = ContextSummary(**parsed_data)

                logger.info("Successfully parsed LLM response into ContextSummary")

            except (json.JSONDecodeError, ValueError, TypeError) as e:
                logger.warning(f"Failed to parse LLM response: {e}")
                logger.warning(f"Raw response: {response.content}")

                # Return empty context summary if parsing fails
                logger.info("Using empty ContextSummary due to parsing failure")
                context_summary = ContextSummary(
                    deal_summary={
                        "coverage_terms": "",
                        "risk_profile": "",
                        "premium_structure": "",
                        "line_of_business": "",
                        "territory": "",
                        "key_risk_factors": [],
                        "current_offer_details": "",
                    },
                    client_summary={
                        "relationship_duration": "",
                        "prior_negotiation_history": [],
                        "claim_history": "",
                        "payment_history": "",
                        "negotiation_style": "",
                    },
                    negotiation_context={
                        "current_objections": [],
                        "discussion_progress": [],
                        "offer_history": [],
                        "client_priorities": [],
                    },
                    comparable_deals={
                        "similar_deals": [],
                        "market_trends": "",
                        "benchmark_insights": "",
                    },
                    relevant_domain_knowledge=[],
                    key_insights=[],
                )

            # Add performance metadata
            end_time = datetime.now(UTC)
            trace = add_performance_metadata(
                trace,
                start_time,
                end_time,
                {
                    "context_summary_created": True,
                    "domain_knowledge_items": len(state.domain_knowledge),
                    "parsing_successful": hasattr(context_summary, "deal_summary"),
                },
            )

            logger.info("=== Completed analyze_context node ===")
            log_state(state, "Output ")

            # Update state with context summary
            state.context_summary = context_summary
            return state

        except Exception as e:
            logger.error(f"Error in analyze_context: {str(e)}")
            trace = add_error_metadata(
                trace,
                str(e),
                {"state_keys": list(state.__dict__.keys()) if state else []},
            )
            raise

    return analyze_context
