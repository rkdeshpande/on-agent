"""Trace metadata utilities for the offer negotiation agent.

This module provides utilities for adding structured metadata to traces,
enabling better observability and debugging of the agent's execution.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


def _get_state_value(state, key, default=None):
    if hasattr(state, key):
        return getattr(state, key)
    if isinstance(state, dict):
        return state.get(key, default)
    return default


def _has_state_key(state, key):
    if hasattr(state, key):
        return True
    if isinstance(state, dict):
        return key in state
    return False


def create_trace_metadata(
    node_name: str,
    state: Any,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create structured trace metadata for a node execution.

    Args:
        node_name: Name of the node being executed
        state: Current state of the graph
        additional_metadata: Any additional metadata to include

    Returns:
        Dictionary containing structured trace metadata
    """
    metadata = {
        "timestamp": datetime.utcnow().isoformat(),
        "node": node_name,
        "state_summary": {
            "deal_id": _get_state_value(state, "deal_id", "unknown"),
            "has_domain_chunks": bool(_get_state_value(state, "domain_chunks")),
            "has_strategy": bool(_get_state_value(state, "strategy")),
            "has_rationale": bool(_get_state_value(state, "rationale")),
        },
    }

    # Add information needs if present
    if _has_state_key(state, "information_needs"):
        metadata["state_summary"]["information_needs"] = _get_state_value(
            state, "information_needs"
        )

    # Add decision basis if present
    if _has_state_key(state, "decision_basis"):
        metadata["state_summary"]["decision_basis"] = [
            {
                "heuristic": decision["heuristic"],
                "confidence": decision["confidence"],
            }
            for decision in _get_state_value(state, "decision_basis")
        ]

    # Add any additional metadata
    if additional_metadata:
        metadata.update(additional_metadata)

    return metadata


def add_error_metadata(
    metadata: Dict[str, Any],
    error: Exception,
    error_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Add error information to trace metadata.

    Args:
        metadata: Existing trace metadata
        error: The exception that occurred
        error_context: Additional context about the error

    Returns:
        Updated metadata dictionary with error information
    """
    error_metadata = {
        "error": {
            "type": error.__class__.__name__,
            "message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
        }
    }

    if error_context:
        error_metadata["error"]["context"] = error_context

    return {**metadata, **error_metadata}


def add_performance_metadata(
    metadata: Dict[str, Any],
    start_time: datetime,
    end_time: datetime,
    metrics: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Add performance metrics to trace metadata.

    Args:
        metadata: Existing trace metadata
        start_time: When the operation started
        end_time: When the operation ended
        metrics: Additional performance metrics

    Returns:
        Updated metadata dictionary with performance information
    """
    duration = (end_time - start_time).total_seconds()

    performance_metadata = {
        "performance": {
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }
    }

    if metrics:
        performance_metadata["performance"]["metrics"] = metrics

    return {**metadata, **performance_metadata}
