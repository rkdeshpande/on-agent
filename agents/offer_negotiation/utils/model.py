import os

import yaml
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from config.app_config import config


def get_llm():
    """Get the LLM instance."""
    # Load model settings from YAML using config path
    with open(config.model_settings_path, "r") as f:
        settings = yaml.safe_load(f)

    # Get model kwargs, removing any None values
    model_kwargs = {k: v for k, v in settings["model_kwargs"].items() if v is not None}

    provider = settings.get("provider", "openai")
    model = settings["model"]

    if provider == "ollama":
        return ChatOllama(model=model, **model_kwargs)
    else:
        return ChatOpenAI(model=model, **model_kwargs)
