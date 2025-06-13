import logging
from typing import Callable

from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from agents.offer_negotiation.core.models.deal_models import DealContext
from agents.offer_negotiation.graph.state import DomainKnowledgeState, StrategyState
from agents.offer_negotiation.utils.model import get_llm

logger = logging.getLogger(__name__)


def create_generate_strategy_node() -> Callable:
    """Create a node that generates a negotiation strategy based on deal context and domain knowledge."""

    # Get the LLM
    llm = get_llm()

    # Create the prompt template
    strategy_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert insurance negotiator. Your task is to generate a negotiation strategy based on the deal context and domain knowledge.

Deal Context:
{deal_context}

Domain Knowledge:
{domain_knowledge}

Generate a detailed negotiation strategy that:
1. Addresses the client's objections
2. Leverages the client's history
3. Uses insights from comparable deals
4. Considers the risk profile
5. Provides specific recommendations for premium and deductible adjustments

Format your response as a structured strategy with clear sections.""",
            ),
            (
                "human",
                "Please generate a negotiation strategy based on the provided context.",
            ),
        ]
    )

    @traceable(name="generate_strategy", run_type="chain")
    def generate_strategy(state: DomainKnowledgeState) -> StrategyState:
        logger.info("=== Starting generate_strategy node ===")
        logger.debug(f"Input state: {state}")

        # Extract deal context
        deal_context = DealContext(**state["deal_context"])

        # Format domain knowledge
        domain_knowledge = "\n".join(
            [
                f"- {chunk['content']} (Source: {chunk['metadata']['document_type']})"
                for chunk in state["domain_chunks"]
            ]
        )

        # Generate strategy using LLM
        chain = strategy_prompt | llm
        response = chain.invoke(
            {
                "deal_context": deal_context.model_dump_json(indent=2),
                "domain_knowledge": domain_knowledge
                or "No specific domain knowledge available.",
            }
        )

        strategy = response.content
        logger.info(f"Generated strategy: {strategy}")

        # Update state
        updated_state: StrategyState = {
            **state,
            "strategy": strategy,
        }

        logger.info("=== Completed generate_strategy node ===")
        logger.debug(f"Output state: {updated_state}")

        return updated_state

    return generate_strategy
