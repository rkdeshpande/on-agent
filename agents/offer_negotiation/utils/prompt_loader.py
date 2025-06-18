import os
from pathlib import Path

from config.app_config import config


def load_prompt(filename: str) -> str:
    """Load a prompt template from the config/prompts directory.

    Args:
        filename: Name of the prompt file (e.g., "strategy_generation.md")

    Returns:
        str: Contents of the prompt file
    """
    prompt_path = config.prompts_dir / filename

    with open(prompt_path, "r") as f:
        return f.read()
