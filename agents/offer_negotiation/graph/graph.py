from langgraph.graph import END, StateGraph

from agents.offer_negotiation.core.repositories.mock_deal_repository import (
    MockDealRepository,
)
from agents.offer_negotiation.graph.nodes.analyze_context_node import (
    create_analyze_context_node,
)
from agents.offer_negotiation.graph.nodes.fetch_deal_context_node import (
    create_fetch_deal_context_node,
)
from agents.offer_negotiation.graph.nodes.fetch_domain_knowledge_node import (
    create_fetch_domain_knowledge_node,
)
from agents.offer_negotiation.graph.nodes.identify_information_gaps_node import (
    create_identify_information_gaps_node,
)
from agents.offer_negotiation.graph.nodes.select_relevant_knowledge_node import (
    create_select_relevant_knowledge_node,
)
from agents.offer_negotiation.graph.state import AgentState
from agents.offer_negotiation.knowledge.domain_documents import DocumentType
from agents.offer_negotiation.knowledge.domain_knowledge_base import DomainKnowledgeBase

# from agents.offer_negotiation.graph.nodes.generate_rationale_node import (
#     create_generate_rationale_node,
# )
# from agents.offer_negotiation.graph.nodes.generate_strategies_node import (
#     create_generate_strategies_node,
# )


def create_agent_graph(
    deal_repo: MockDealRepository,
    knowledge_base: DomainKnowledgeBase,
) -> StateGraph:
    """
    Create the complete agent graph with structured output nodes.

    GRAPH FLOW:
    ===========
    1. fetch_deal_context      - Gets deal data from repository
    2. fetch_domain_knowledge  - Loads all domain knowledge chunks
    3. analyze_context         - Creates comprehensive ContextSummary
    4. select_relevant_knowledge - Filters domain knowledge to only relevant items
    5. identify_information_gaps - Analyzes missing data, creates prioritized gap list
    6. generate_strategies     - Creates 3 structured strategies (Conservative/Moderate/Aggressive)
    7. generate_rationale      - Creates detailed rationale for each strategy

    Each node receives the complete AgentState and adds/updates specific fields,
    creating a rich, structured output for negotiation decision-making.
    """

    print("=== CREATING AGENT GRAPH ===")

    # Create the graph
    workflow = StateGraph(AgentState)

    # Input nodes - fetch raw data
    print("Adding fetch_deal_context node...")
    workflow.add_node("fetch_deal_context", create_fetch_deal_context_node(deal_repo))

    print("Adding fetch_domain_knowledge node...")
    workflow.add_node(
        "fetch_domain_knowledge", create_fetch_domain_knowledge_node(knowledge_base)
    )

    # Analysis node - creates structured output
    print("Adding analyze_context node...")
    workflow.add_node("analyze_context", create_analyze_context_node())

    # Knowledge selection node - filters domain knowledge
    print("Adding select_relevant_knowledge node...")
    workflow.add_node(
        "select_relevant_knowledge", create_select_relevant_knowledge_node()
    )

    # Information gaps analysis node - identifies missing data
    print("Adding identify_information_gaps node...")
    workflow.add_node(
        "identify_information_gaps", create_identify_information_gaps_node()
    )

    # Future nodes (commented out for now)
    # workflow.add_node("generate_strategies", create_generate_strategies_node())
    # workflow.add_node("generate_rationale", create_generate_rationale_node())

    # Define the flow
    print("Setting up graph flow...")
    workflow.set_entry_point("fetch_deal_context")
    workflow.add_edge("fetch_deal_context", "fetch_domain_knowledge")
    workflow.add_edge("fetch_domain_knowledge", "analyze_context")
    workflow.add_edge("analyze_context", "select_relevant_knowledge")
    workflow.add_edge("select_relevant_knowledge", "identify_information_gaps")
    workflow.add_edge("identify_information_gaps", END)

    print("=== GRAPH CREATION COMPLETE ===")

    # Future edges (commented out for now)
    # workflow.add_edge("identify_information_gaps", "generate_strategies")
    # workflow.add_edge("generate_strategies", "generate_rationale")
    # workflow.add_edge("generate_rationale", END)

    return workflow
