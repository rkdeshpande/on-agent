import json
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from langsmith import Client


def export_recent_traces(hours=1):
    """Export recent traces from LangSmith."""
    # Load environment variables from secrets.env
    load_dotenv("config/secrets.env")

    if not os.getenv("LANGCHAIN_API_KEY"):
        print("Please set LANGCHAIN_API_KEY environment variable in secrets.env")
        return

    client = Client()

    # Get traces from the last hour
    start_time = datetime.now() - timedelta(hours=hours)
    project_name = os.getenv("LANGCHAIN_PROJECT", "OfferNegotiationAgent")
    traces = client.list_runs(project_name=project_name, start_time=start_time)

    # Group runs by trace
    trace_runs = {}
    for run in traces:
        if run.trace_id not in trace_runs:
            trace_runs[run.trace_id] = []
        trace_runs[run.trace_id].append(run)

    # Export each trace
    for trace_id, runs in trace_runs.items():
        print(f"\n=== Trace {trace_id} ===")

        for run in runs:
            print(f"\n--- Run: {run.name} ---")
            print(f"Input: {json.dumps(run.inputs, indent=2)}")
            print(f"Output: {json.dumps(run.outputs, indent=2)}")
            if run.error:
                print(f"Error: {run.error}")
            print(
                f"Duration: {run.end_time - run.start_time if run.end_time else 'Not completed'}"
            )
            print("-" * 80)


if __name__ == "__main__":
    export_recent_traces()
