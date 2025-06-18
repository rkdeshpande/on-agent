import logging
import os

from agents.offer_negotiation.core.repositories.mock_deal_repository import (
    MockDealRepository,
)
from agents.offer_negotiation.graph.graph import create_agent_graph
from agents.offer_negotiation.graph.state import AgentState
from agents.offer_negotiation.knowledge.domain_documents import (
    DocumentProcessor,
    load_domain_documents,
)
from agents.offer_negotiation.knowledge.domain_knowledge_base import DomainKnowledgeBase
from agents.offer_negotiation.utils.logging import setup_logging
from config.app_config import config

# Configure logging
logger = logging.getLogger(__name__)
setup_logging()


def run_agent(
    deal_id: str,
    model_settings: dict = None,
) -> dict:
    """Run the graph-based negotiation agent and return the final state."""
    # Set the project name for LangSmith using config
    os.environ["LANGCHAIN_PROJECT"] = config.langchain_project

    # Set up repositories and knowledge base
    deal_repo = MockDealRepository()
    knowledge_base = DomainKnowledgeBase()

    # Load and process domain documents
    processor = DocumentProcessor()
    documents = load_domain_documents()
    for doc in documents:
        chunks = processor.parse(doc)
        knowledge_base.add_document_chunks(chunks)
    logger.info(f"Loaded {len(documents)} domain documents into knowledge base")

    # Create the agent graph
    agent_graph = create_agent_graph(deal_repo, knowledge_base).compile()

    # Prepare initial state for the graph
    initial_state = AgentState(
        deal_id=deal_id,
        deal_context={},
        domain_knowledge=[],
        reasoning_steps=[],
        reasoning_output={},
    )

    # Run the graph
    result = agent_graph.invoke(initial_state)

    final_state = AgentState(**result)
    return final_state.to_dict()
