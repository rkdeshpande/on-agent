import os
from pathlib import Path


def load_prompt(filename: str) -> str:
    """Load a prompt template from the config/prompts directory.

    Args:
        filename: Name of the prompt file (e.g., "strategy_generation.md")

    Returns:
        str: Contents of the prompt file
    """
    # Get the project root directory (where config/ is located)
    project_root = Path(__file__).parent.parent.parent.parent
    prompt_path = project_root / "config" / "prompts" / filename

    with open(prompt_path, "r") as f:
        return f.read()
