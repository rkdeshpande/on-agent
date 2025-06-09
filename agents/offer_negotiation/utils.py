from typing import Any, Dict

import yaml
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI


def load_model_settings() -> Dict[str, Any]:
    """
    Load model settings from config file.

    Returns:
        Dictionary containing model settings
    """
    with open("config/model_settings.yaml", "r") as f:
        return yaml.safe_load(f)


def get_llm():
    """
    Initialize and return the appropriate LLM based on settings.

    Returns:
        An instance of either ChatOpenAI or ChatOllama
    """
    settings = load_model_settings()
    provider = settings["provider"]
    model_name = settings["model"]
    model_kwargs = settings.get("model_kwargs", {})

    if provider == "openai":
        return ChatOpenAI(model=model_name, **model_kwargs)
    elif provider == "ollama":
        return ChatOllama(model=model_name, model_kwargs=model_kwargs)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
