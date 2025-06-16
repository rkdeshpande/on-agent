"""Node interfaces for the offer negotiation agent.

This module defines the interfaces for all nodes in the offer negotiation agent graph.
Each interface is annotated with AIP metadata to enable proper node execution and tracing.
"""

from typing import Any, Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field


class NodeMetadata(BaseModel):
    """Metadata for a node in the graph."""

    name: str = Field(..., description="Name of the node")
    description: str = Field(..., description="Description of what the node does")
    input_schema: Dict[str, Any] = Field(..., description="Schema of the input state")
    output_schema: Dict[str, Any] = Field(..., description="Schema of the output state")
    required_fields: List[str] = Field(
        default_factory=list, description="Required fields in the input state"
    )
    optional_fields: List[str] = Field(
        default_factory=list, description="Optional fields in the input state"
    )


# Node Interfaces
IDENTIFY_INFORMATION_NEEDS_METADATA = NodeMetadata(
    name="identify_information_needs",
    description="Identifies information needs from the deal context",
    input_schema={
        "deal_context": Dict[str, Any],
        "domain_knowledge": List[Dict[str, Any]],
    },
    output_schema={
        "deal_context": Dict[str, Any],
        "domain_knowledge": List[Dict[str, Any]],
        "information_needs": List[str],
    },
    required_fields=["deal_context"],
    optional_fields=["domain_knowledge"],
)


RETRIEVE_DOMAIN_KNOWLEDGE_METADATA = NodeMetadata(
    name="retrieve_domain_knowledge",
    description="Retrieves relevant domain knowledge based on information needs",
    input_schema={
        "deal_context": Dict[str, Any],
        "information_needs": List[str],
    },
    output_schema={
        "deal_context": Dict[str, Any],
        "information_needs": List[str],
        "domain_knowledge": List[Dict[str, Any]],
    },
    required_fields=["deal_context", "information_needs"],
)


GENERATE_STRATEGY_METADATA = NodeMetadata(
    name="generate_strategy",
    description="Generates a negotiation strategy based on deal context and domain knowledge",
    input_schema={
        "deal_context": Dict[str, Any],
        "domain_knowledge": List[Dict[str, Any]],
    },
    output_schema={
        "deal_context": Dict[str, Any],
        "domain_knowledge": List[Dict[str, Any]],
        "strategy": str,
        "decision_basis": List[Dict[str, str]],
    },
    required_fields=["deal_context", "domain_knowledge"],
)


EXPLAIN_RATIONALE_METADATA = NodeMetadata(
    name="explain_rationale",
    description="Explains the rationale behind the generated strategy",
    input_schema={
        "deal_context": Dict[str, Any],
        "domain_knowledge": List[Dict[str, Any]],
        "strategy": str,
        "decision_basis": List[Dict[str, str]],
    },
    output_schema={
        "deal_context": Dict[str, Any],
        "domain_knowledge": List[Dict[str, Any]],
        "strategy": str,
        "decision_basis": List[Dict[str, str]],
        "rationale": str,
        "reasoning_steps": List[str],
    },
    required_fields=["deal_context", "strategy"],
    optional_fields=["domain_knowledge", "decision_basis"],
)
