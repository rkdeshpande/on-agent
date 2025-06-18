import os

import yaml
from langchain_openai import ChatOpenAI

from config.app_config import config


def get_llm():
    """Get the LLM instance."""
    # Load model settings from YAML using config path
    with open(config.model_settings_path, "r") as f:
        settings = yaml.safe_load(f)

    # Get model kwargs, removing any None values
    model_kwargs = {k: v for k, v in settings["model_kwargs"].items() if v is not None}

    return ChatOpenAI(model=settings["model"], **model_kwargs)
