import json
from typing import Any, Dict, List, Set, Union


def prepare_for_json(obj: Any) -> Any:
    """Convert non-JSON-serializable types to JSON-serializable ones."""
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: prepare_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [prepare_for_json(item) for item in obj]
    return obj


def log_state(state: Any, prefix: str = "") -> None:
    """Safely log a state object with JSON serialization."""
    import logging

    logger = logging.getLogger(__name__)
    logger.info(
        f"{prefix}state: {json.dumps(prepare_for_json(state.model_dump()), indent=2)}"
    )
