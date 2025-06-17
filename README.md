# Offer & Negotiation Agent

This project implements an agent for handling offer and negotiation processes using LangGraph and LangChain. The agent fetches past rationale, reasons about the negotiation context, and logs the rationale for further analysis.

## Features

- **Fetch Context**: Retrieves past rationale for a given deal ID.
- **Reason**: Generates a negotiation strategy based on the past rationale.
- **Log Rationale**: Logs the reasoning process for future reference.

## Quick Start

1. **Prerequisites**
   - Python 3.8 or higher
   - pip (Python package installer)

2. **Create a Virtual Environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Agent**

   ```bash
   python run.py
   ```

   This will execute the agent with a predefined deal ID and print the output.