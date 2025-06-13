import logging
import os

from agents.offer_negotiation.core.repositories.mock_deal_repository import (
    MockDealRepository,
)
from agents.offer_negotiation.graph.graph import create_agent_graph
from agents.offer_negotiation.knowledge.domain_knowledge_base import DomainKnowledgeBase
from agents.offer_negotiation.utils.logging import setup_logging

# Configure logging
logger = logging.getLogger(__name__)
setup_logging()


def run_agent(
    deal_id: str,
    model_settings: dict = None,
) -> dict:
    """Run the graph-based negotiation agent and return the final state."""
    # Set the project name for LangSmith
    os.environ["LANGCHAIN_PROJECT"] = os.getenv(
        "LANGCHAIN_PROJECT", "OfferNegotiationAgent"
    )

    # Set up repositories and knowledge base (mock for now)
    deal_repo = MockDealRepository()
    knowledge_base = DomainKnowledgeBase()

    # Create the agent graph
    agent_graph = create_agent_graph(deal_repo, knowledge_base).compile()

    # Prepare initial state for the graph
    initial_state = {
        "deal_id": deal_id,
        "deal_context": {},
        "domain_chunks": [],
        "reasoning_steps": [],
        "reasoning_output": {},  # Initialize empty reasoning output
    }

    # Run the graph
    result = agent_graph.invoke(initial_state)
    return result
