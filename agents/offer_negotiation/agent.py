from typing import Any, Dict

from langgraph.graph import StateGraph

from .communication import get_past_rationale
from .reasoning import generate_negotiation_strategy

# Define the state type for our graph
State = Dict[str, Any]


def fetch_context(state: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch relevant context for the negotiation."""
    print("Node: fetch_context")
    print(f"Input state: {state}")

    # Get past rationale for the deal
    deal_id = state["deal_id"]
    past_rationale = get_past_rationale(deal_id)

    # Return the full state, merging past_rationale
    return {"past_rationale": past_rationale}


def reason(state: Dict[str, Any]) -> Dict[str, Any]:
    """Reason about the negotiation context."""
    print("Node: reason")
    print(f"Input state: {state}")

    # Generate negotiation strategy
    past_rationale = state["past_rationale"]
    strategy = generate_negotiation_strategy(past_rationale)

    # Merge the strategy result with the existing state
    return {"strategy": strategy}


def log_rationale(state: Dict[str, Any]) -> Dict[str, Any]:
    """Log the reasoning process."""
    print("Node: log_rationale")
    print(f"Input state: {state}")
    strategy = state["strategy"]
    print(f"Logging rationale: {strategy}")
    # Return the full state unchanged
    return state


def create_agent() -> StateGraph:
    workflow = StateGraph()
    workflow.add_node("fetch_context", fetch_context)
    workflow.add_node("reason", reason)
    workflow.add_node("log_rationale", log_rationale)
    workflow.add_edge("fetch_context", "reason")
    workflow.add_edge("reason", "log_rationale")
    return workflow


def run_agent(deal_id: str) -> Dict[str, Any]:
    """
    Run the negotiation agent with the given input.

    Args:
        deal_id: The ID of the deal

    Returns:
        Dictionary containing the final state after running the graph
    """
    agent = create_agent()
    result = agent.invoke({"deal_id": deal_id})
    return result
