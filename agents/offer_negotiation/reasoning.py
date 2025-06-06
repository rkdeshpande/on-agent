import yaml
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# Initialize model once at module level
model = ChatOllama(model="mistral")


def load_prompt_template():
    with open("config/prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)
    return prompts["negotiation_strategy"]


def generate_negotiation_strategy(state: dict) -> dict:
    """
    Generate a negotiation strategy based on the structured context.

    Args:
        state: The current state of the agent

    Returns:
        Dictionary containing the strategy and rationale
    """
    # Load and format the prompt
    prompt_template = load_prompt_template()
    prompt = ChatPromptTemplate.from_template(prompt_template)
    formatted_prompt = prompt.format(
        structured_context=state["structured_context"],
        past_rationale=state["past_rationale"],
    )

    # Generate the response
    print("\nGenerating negotiation strategy...")
    response = model.invoke(formatted_prompt)
    print(f"Generated response: {response}")

    # Parse the response into the structured format
    # For now, we'll return a placeholder structure
    # TODO: Add proper JSON parsing
    return {
        "strategy": "Placeholder strategy",
        "talking_points": ["Point 1", "Point 2", "Point 3"],
        "rationale_summary": "Placeholder rationale summary",
        "detailed_rationale": "Placeholder detailed rationale",
        "ci_log_success": True,
    }
