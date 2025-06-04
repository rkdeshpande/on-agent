from typing import Dict, Any
from langgraph.graph import Graph, StateGraph
from .communication import get_past_rationale
from .reasoning import generate_negotiation_strategy

# Define the state type for our graph
State = Dict[str, Any]

def fetch_context(state: State) -> State:
    """Fetch relevant context for the negotiation."""
    print("Node: fetch_context")
    print(f"Input state: {state}")
    
    # Get past rationale for the deal
    deal_id = state["deal_id"]
    past_rationale = get_past_rationale(deal_id)
    
    # Return the full state, merging past_rationale
    return {**state, "past_rationale": past_rationale.get("past_rationale", [])}

def reason(state: State) -> State:
    """Reason about the negotiation context."""
    print("Node: reason")
    print(f"Input state: {state}")
    
    # Generate negotiation strategy
    strategy_result = generate_negotiation_strategy(state)
    
    # Merge the strategy result with the existing state
    return {**state, **strategy_result}

def log_rationale(state: State) -> State:
    """Log the reasoning process."""
    print("Node: log_rationale")
    print(f"Input state: {state}")
    # Return the full state unchanged
    return state

# Create the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("fetch_context", fetch_context)
workflow.add_node("reason", reason)
workflow.add_node("log_rationale", log_rationale)

# Set entry point
workflow.set_entry_point("fetch_context")

# Add edges
workflow.add_edge("fetch_context", "reason")
workflow.add_edge("reason", "log_rationale")

# Compile the graph
agent = workflow.compile()

def run_agent(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the negotiation agent with the given input.
    
    Args:
        input_data: Dictionary containing the input state
        
    Returns:
        Dictionary containing the final state after running the graph
    """
    return agent.invoke(input_data)
