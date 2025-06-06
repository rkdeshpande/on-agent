from typing import Optional, TypedDict

import yaml
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph

from .communication import get_past_rationale
from .memory import load_submission_context
from .reasoning import generate_negotiation_strategy

# Initialize model once at module level
model = ChatOllama(model="mistral")


class StructuredContext(TypedDict):
    broker_position: str
    exposure_changes: str
    price_arguments: str
    quote_constraints: dict[str, str]
    negotiation_history: str


class AgentState(TypedDict):
    deal_id: str
    submission_id: str | None
    past_rationale: str
    submission_notes: dict[str, str]
    structured_context: StructuredContext | None
    talking_points: list[str] | None
    strategy: str | None
    rationale_summary: str | None
    detailed_rationale: str | None
    ci_log_success: bool | None


def load_prompt_template(prompt_name: str) -> str:
    """Load a prompt template from prompts.yaml."""
    with open("config/prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)
    return prompts[prompt_name]


def fetch_context(state: AgentState) -> AgentState:
    """Fetch relevant context for the negotiation."""
    print("\n=== Executing fetch_context node ===")
    print(f"Input state: {state}")

    # Get past rationale for the deal
    deal_id = state["deal_id"]
    print(f"\nFetching past rationale for deal: {deal_id}")
    past_rationale = get_past_rationale(deal_id)
    print(
        f"Past rationale received: {past_rationale[:100]}..."
        if past_rationale
        else "No past rationale found"
    )

    # Load submission context if submission_id is provided
    submission_notes = {}
    if "submission_id" in state and state["submission_id"]:
        print(f"\nLoading submission context for ID: {state['submission_id']}")
        submission_notes = load_submission_context(state["submission_id"])
        print(f"Loaded {len(submission_notes)} files")

    # Return the full state, merging past_rationale and submission_notes
    result = {
        **state,
        "past_rationale": past_rationale,
        "submission_notes": submission_notes,
    }
    print("\n=== Completed fetch_context node ===\n")
    return result


def process_file_content(filename: str, content: str) -> Optional[StructuredContext]:
    """
    Process a single file's content to extract structured information.

    Args:
        filename: Name of the file being processed
        content: Content of the file

    Returns:
        StructuredContext with extracted information, or None if processing failed
    """
    if not content.strip():
        print(f"Skipping empty file: {filename}")
        return None

    try:
        # Load and format the prompt
        prompt_template = load_prompt_template("structure_context")
        prompt = ChatPromptTemplate.from_template(prompt_template)
        formatted_prompt = prompt.format(
            submission_notes=content, filename=filename  # Pass filename for debugging
        )

        # Generate the response
        print(f"\nProcessing file: {filename}")
        response = model.invoke(formatted_prompt)
        print(f"Generated response for {filename}: {response}")

        # Parse the response into the structured format
        # For now, we'll return a placeholder structure
        # TODO: Add proper JSON parsing
        return {
            "broker_position": (f"From {filename}: Extracted broker position"),
            "exposure_changes": (f"From {filename}: Extracted exposure changes"),
            "price_arguments": (f"From {filename}: Extracted price arguments"),
            "quote_constraints": {
                "MFP": f"From {filename}: Extracted MFP",
                "RTP": f"From {filename}: Extracted RTP",
                "WAP": f"From {filename}: Extracted WAP",
            },
            "negotiation_history": (f"From {filename}: Extracted negotiation history"),
        }
    except Exception as e:
        print(f"Error processing file {filename}: {str(e)}")
        return None


def merge_structured_contexts(contexts: list[StructuredContext]) -> StructuredContext:
    """
    Merge multiple structured contexts into one.

    Args:
        contexts: List of structured contexts to merge

    Returns:
        Merged structured context
    """
    if not contexts:
        return {
            "broker_position": "",
            "exposure_changes": "",
            "price_arguments": "",
            "quote_constraints": {"MFP": "", "RTP": "", "WAP": ""},
            "negotiation_history": "",
        }

    # Initialize with empty values
    merged = {
        "broker_position": [],
        "exposure_changes": [],
        "price_arguments": [],
        "quote_constraints": {"MFP": [], "RTP": [], "WAP": []},
        "negotiation_history": [],
    }

    # Collect values from all contexts
    for ctx in contexts:
        if ctx["broker_position"]:
            merged["broker_position"].append(ctx["broker_position"])
        if ctx["exposure_changes"]:
            merged["exposure_changes"].append(ctx["exposure_changes"])
        if ctx["price_arguments"]:
            merged["price_arguments"].append(ctx["price_arguments"])
        if ctx["negotiation_history"]:
            merged["negotiation_history"].append(ctx["negotiation_history"])

        # Handle quote constraints
        for key in ["MFP", "RTP", "WAP"]:
            if ctx["quote_constraints"][key]:
                merged["quote_constraints"][key].append(ctx["quote_constraints"][key])

    # Join all values with separators
    result = {
        "broker_position": (
            "\n---\n".join(merged["broker_position"])
            if merged["broker_position"]
            else ""
        ),
        "exposure_changes": (
            "\n---\n".join(merged["exposure_changes"])
            if merged["exposure_changes"]
            else ""
        ),
        "price_arguments": (
            "\n---\n".join(merged["price_arguments"])
            if merged["price_arguments"]
            else ""
        ),
        "quote_constraints": {
            "MFP": (
                "\n---\n".join(merged["quote_constraints"]["MFP"])
                if merged["quote_constraints"]["MFP"]
                else ""
            ),
            "RTP": (
                "\n---\n".join(merged["quote_constraints"]["RTP"])
                if merged["quote_constraints"]["RTP"]
                else ""
            ),
            "WAP": (
                "\n---\n".join(merged["quote_constraints"]["WAP"])
                if merged["quote_constraints"]["WAP"]
                else ""
            ),
        },
        "negotiation_history": (
            "\n---\n".join(merged["negotiation_history"])
            if merged["negotiation_history"]
            else ""
        ),
    }

    # Validate the result has all required fields
    required_fields = [
        "broker_position",
        "exposure_changes",
        "price_arguments",
        "quote_constraints",
        "negotiation_history",
    ]
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
    assert all(
        key in result["quote_constraints"] for key in ["MFP", "RTP", "WAP"]
    ), "Missing required quote constraint fields"

    return result


def structure_context_node(state: AgentState) -> AgentState:
    """Structure the submission context into organized fields."""
    print("\n=== Executing structure_context node ===")
    print(f"Input state: {state}")

    # Process each file individually
    structured_contexts = []
    for filename, content in state["submission_notes"].items():
        result = process_file_content(filename, content)
        if result:
            structured_contexts.append(result)

    # Merge all results
    print("\nMerging structured contexts...")
    merged_context = merge_structured_contexts(structured_contexts)
    print(f"Merged context: {merged_context}")

    # Return the full state with structured context
    result = {**state, "structured_context": merged_context}
    print("\n=== Completed structure_context node ===\n")
    return result


def reason(state: AgentState) -> AgentState:
    """Reason about the negotiation context."""
    print("\n=== Executing reason node ===")
    print(f"Input state: {state}")

    # Generate negotiation strategy using structured context
    print("\nGenerating negotiation strategy...")
    strategy_result = generate_negotiation_strategy(state)
    print(f"Strategy generated: {strategy_result}")

    # Merge the strategy result with the existing state
    result = {**state, **strategy_result}
    print("\n=== Completed reason node ===\n")
    return result


def log_rationale(state: AgentState) -> AgentState:
    """Log the reasoning process."""
    print("\n=== Executing log_rationale node ===")
    print(f"Input state: {state}")
    print("\nFinal state summary:")
    print(f"- Deal ID: {state['deal_id']}")
    print(f"- Submission ID: {state['submission_id']}")
    print(f"- Strategy: {state['strategy']}")
    print(f"- Talking Points: {state['talking_points']}")
    print(f"- Rationale Summary: {state['rationale_summary']}")
    print("\n=== Completed log_rationale node ===\n")
    return state


def create_agent() -> StateGraph:
    workflow = StateGraph(AgentState)
    workflow.add_node("fetch_context", fetch_context)
    workflow.add_node("structure_context", structure_context_node)
    workflow.add_node("reason", reason)
    workflow.add_node("log_rationale", log_rationale)

    # Set the entry point
    workflow.set_entry_point("fetch_context")

    # Add edges
    workflow.add_edge("fetch_context", "structure_context")
    workflow.add_edge("structure_context", "reason")
    workflow.add_edge("reason", "log_rationale")

    return workflow.compile()


def run_agent(deal_id: str, submission_id: str = None) -> AgentState:
    """
    Run the negotiation agent with the given input.

    Args:
        deal_id: The ID of the deal
        submission_id: Optional ID of the submission to load notes from

    Returns:
        Dictionary containing the final state after running the graph
    """
    input_data: AgentState = {
        "deal_id": deal_id,
        "submission_id": submission_id,
        "past_rationale": "",
        "submission_notes": {},
        "structured_context": None,
        "talking_points": None,
        "strategy": None,
        "rationale_summary": None,
        "detailed_rationale": None,
        "ci_log_success": None,
    }

    agent = create_agent()
    result = agent.invoke(input_data)
    return result
