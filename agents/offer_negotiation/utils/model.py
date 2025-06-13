from langchain_community.chat_models import ChatOllama


def get_llm():
    """Get the LLM instance."""
    return ChatOllama(model="llama2")
