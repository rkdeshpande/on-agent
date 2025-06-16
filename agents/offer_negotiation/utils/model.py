from langchain_ollama import ChatOllama


def get_llm():
    """Get the LLM instance."""
    return ChatOllama(model="mistral")
