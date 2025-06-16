"""Test script to simulate AIP-like node execution.

This script demonstrates how the offer negotiation agent nodes would work in an AIP environment,
including proper state management and trace metadata collection.
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any, Dict, List

from agents.offer_negotiation.core.repositories.mock_deal_repository import (
    MockDealRepository,
)
from agents.offer_negotiation.graph.interfaces import (
    EXPLAIN_RATIONALE_METADATA,
    GENERATE_STRATEGY_METADATA,
    IDENTIFY_INFORMATION_NEEDS_METADATA,
    RETRIEVE_DOMAIN_KNOWLEDGE_METADATA,
)
from agents.offer_negotiation.graph.nodes.explain_rationale_node import (
    create_explain_rationale_node,
)
from agents.offer_negotiation.graph.nodes.generate_strategy_node import (
    create_generate_strategy_node,
)
from agents.offer_negotiation.graph.nodes.identify_information_needs_node import (
    create_identify_information_needs_node,
)
from agents.offer_negotiation.graph.nodes.retrieve_domain_knowledge_node import (
    create_retrieve_domain_knowledge_node,
)
from agents.offer_negotiation.graph.utils import prepare_for_json
from agents.offer_negotiation.knowledge.domain_knowledge_base import DomainKnowledgeBase
from agents.offer_negotiation.utils.trace_metadata import (
    add_error_metadata,
    add_performance_metadata,
    create_trace_metadata,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIPNodeExecutor:
    """Simulates AIP-like node execution with proper state management and tracing."""

    def __init__(self):
        """Initialize the executor with required dependencies."""
        self.deal_repo = MockDealRepository()
        self.knowledge_base = DomainKnowledgeBase()

        # Create node instances
        self.identify_needs_node = create_identify_information_needs_node()
        self.retrieve_knowledge_node = create_retrieve_domain_knowledge_node(
            self.knowledge_base
        )
        self.generate_strategy_node = create_generate_strategy_node()
        self.explain_rationale_node = create_explain_rationale_node()

        # Store execution traces
        self.traces: List[Dict[str, Any]] = []

    def execute_node(
        self,
        node_name: str,
        node_func: callable,
        state: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a node with proper tracing and error handling.

        Args:
            node_name: Name of the node being executed
            node_func: The node function to execute
            state: Current state of the graph
            metadata: Node metadata from interfaces

        Returns:
            Updated state after node execution

        Raises:
            Exception: If node execution fails
        """
        start_time = datetime.now(UTC)
        trace = create_trace_metadata(node_name, state)

        try:
            # Execute the node
            updated_state = node_func(state)

            # Add performance metadata
            end_time = datetime.now(UTC)
            trace = add_performance_metadata(
                trace,
                start_time,
                end_time,
                metrics={
                    "state_size": len(json.dumps(prepare_for_json(state))),
                    "updated_state_size": len(
                        json.dumps(prepare_for_json(updated_state))
                    ),
                },
            )

            # Store the trace
            self.traces.append(trace)

            return updated_state

        except Exception as e:
            # Add error metadata
            trace = add_error_metadata(
                trace,
                e,
                error_context={"state_keys": list(state.__dict__.keys())},
            )
            self.traces.append(trace)
            raise

    def execute_workflow(self, deal_id: str) -> Dict[str, Any]:
        """Execute the complete workflow for a deal."""
        logging.info(f"Starting workflow execution for deal {deal_id}")

        # Initialize state
        state = {
            "deal_id": deal_id,
            "deal_context": self.deal_repo.get_deal(deal_id),
            "execution_traces": [],
        }

        # Execute nodes in sequence
        start_time = datetime.now(UTC)

        # 1. Identify Information Needs
        state = self.execute_node(
            IDENTIFY_INFORMATION_NEEDS_METADATA.name,
            self.identify_needs_node,
            state,
            IDENTIFY_INFORMATION_NEEDS_METADATA.model_dump(),
        )

        # 2. Retrieve Domain Knowledge
        state = self.execute_node(
            RETRIEVE_DOMAIN_KNOWLEDGE_METADATA.name,
            self.retrieve_knowledge_node,
            state,
            RETRIEVE_DOMAIN_KNOWLEDGE_METADATA.model_dump(),
        )

        # 3. Generate Strategy
        state = self.execute_node(
            GENERATE_STRATEGY_METADATA.name,
            self.generate_strategy_node,
            state,
            GENERATE_STRATEGY_METADATA.model_dump(),
        )

        # 4. Explain Rationale
        state = self.execute_node(
            EXPLAIN_RATIONALE_METADATA.name,
            self.explain_rationale_node,
            state,
            EXPLAIN_RATIONALE_METADATA.model_dump(),
        )

        end_time = datetime.now(UTC)

        # Add workflow-level metadata
        state["execution_traces"].append(
            {
                "workflow": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": (end_time - start_time).total_seconds(),
                    "nodes_executed": len(state["execution_traces"]),
                }
            }
        )

        logging.info("Workflow execution completed successfully")
        return state


def test_aip_execution():
    """Test the AIP-like node execution with a sample deal."""
    executor = AIPNodeExecutor()

    # Execute workflow with a sample deal
    final_state = executor.execute_workflow("DEAL001")

    # Verify final state
    assert "strategy" in final_state
    assert "rationale" in final_state
    assert "reasoning_steps" in final_state

    # Verify traces
    assert len(executor.traces) == 4  # One trace per node
    for trace in executor.traces:
        assert "timestamp" in trace
        assert "node" in trace
        assert "state_summary" in trace
        assert "performance" in trace


if __name__ == "__main__":
    test_aip_execution()
