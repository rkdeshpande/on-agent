from typing import Dict, Any
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
import yaml

def generate_negotiation_strategy(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a negotiation strategy using the local Mistral model via Ollama.
    
    Args:
        input: Dictionary containing deal_id and past_rationale
        
    Returns:
        Dictionary containing talking_points, strategy, rationale_summary, and detailed_rationale
    """
    # Initialize the LLM
    llm = ChatOllama(model="mistral")
    
    # Load prompt template from YAML
    with open("config/prompts.yaml", "r") as f:
        prompt_config = yaml.safe_load(f)
    
    # Construct the prompt using the loaded template
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_config["system"]),
        ("user", prompt_config["user"].format(
            deal_id=input["deal_id"],
            past_rationale=input.get("past_rationale", [])
        ))
    ])
    
    # Get response from LLM
    response = llm.invoke(prompt)
    
    # Parse the response into structured format
    # For now, we'll use a simple parsing approach
    content = response.content
    
    # Split the content into sections
    sections = content.split("\n\n")
    
    # Extract talking points (assuming they're bullet points)
    talking_points = [point.strip("- ").strip() for point in sections[0].split("\n") if point.strip().startswith("-")]
    
    # Extract strategy (assuming it's labeled)
    strategy = sections[1].split(":", 1)[1].strip() if ":" in sections[1] else sections[1].strip()
    
    # Extract rationale summary
    rationale_summary = sections[2].strip()
    
    # Extract detailed rationale
    detailed_rationale = sections[3].strip()
    
    return {
        "talking_points": talking_points,
        "strategy": strategy,
        "rationale_summary": rationale_summary,
        "detailed_rationale": detailed_rationale
    }
