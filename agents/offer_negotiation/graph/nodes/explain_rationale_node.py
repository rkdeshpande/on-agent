import logging
from typing import Callable

from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from agents.offer_negotiation.graph.state import FinalState, StrategyState
from agents.offer_negotiation.utils.model import get_llm

logger = logging.getLogger(__name__)


def create_explain_rationale_node() -> Callable:
    """Create a node that explains the rationale behind the strategy."""

    # Get the LLM
    llm = get_llm()

    # Create the prompt template
    rationale_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert insurance negotiator. Your task is to explain the rationale behind the proposed negotiation strategy.

Deal Context:
{deal_context}

Strategy:
{strategy}

Domain Knowledge Used:
{domain_knowledge}

Explain the rationale for this strategy by:
1. Connecting each strategic element to specific aspects of the deal context
2. Explaining how the strategy addresses the client's objections
3. Justifying the premium and deductible recommendations
4. Highlighting how the strategy leverages client history and comparable deals
5. Addressing any risk considerations

Format your response as a clear, logical explanation that could be presented to stakeholders.""",
            ),
            ("human", "Please explain the rationale behind this negotiation strategy."),
        ]
    )

    @traceable(name="explain_rationale", run_type="chain")
    def explain_rationale(state: StrategyState) -> FinalState:
        logger.info("=== Starting explain_rationale node ===")
        logger.debug(f"Input state: {state}")

        # Format domain knowledge
        domain_knowledge = "\n".join(
            [
                f"- {chunk['content']} (Source: {chunk['metadata']['document_type']})"
                for chunk in state["domain_chunks"]
            ]
        )

        # Generate rationale using LLM
        chain = rationale_prompt | llm
        response = chain.invoke(
            {
                "deal_context": state["deal_context"],
                "strategy": state["strategy"],
                "domain_knowledge": domain_knowledge
                or "No specific domain knowledge available.",
            }
        )

        rationale = response.content
        logger.info(f"Generated rationale: {rationale}")

        # Update state
        updated_state: FinalState = {
            **state,
            "rationale": rationale,
        }

        logger.info("=== Completed explain_rationale node ===")
        logger.debug(f"Output state: {updated_state}")

        return updated_state

    return explain_rationale
