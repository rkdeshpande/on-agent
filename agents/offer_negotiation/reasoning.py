import yaml
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


def load_prompt_template():
    with open("config/prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)
    return prompts["negotiation_strategy"]


def generate_negotiation_strategy(past_rationale: list) -> dict:
    # Load the prompt template
    prompt_template = load_prompt_template()
    prompt = ChatPromptTemplate.from_template(prompt_template)

    # Initialize the model
    model = ChatOllama(model="llama2")

    # Construct the prompt with past rationale
    formatted_prompt = prompt.format(past_rationale=past_rationale)

    # Generate the response
    response = model.invoke(formatted_prompt)
    print(f"Generated response: {response}")

    # Parse the response to extract the required fields
    # This is a placeholder for actual parsing logic
    return {
        "talking_points": ["Point 1", "Point 2"],
        "strategy": "Strategy details",
        "rationale_summary": "Summary of rationale",
        "detailed_rationale": "Detailed explanation",
    }
