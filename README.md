# Offer & Negotiation Agent

This project implements an agent for handling offer and negotiation processes using LangGraph and LangChain. The agent fetches past rationale, reasons about the negotiation context, and logs the rationale for further analysis.

## Features

- **Fetch Context**: Retrieves past rationale for a given deal ID.
- **Reason**: Generates a negotiation strategy based on the past rationale.
- **Log Rationale**: Logs the reasoning process for future reference.

## Installation

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Pre-commit Hooks**

   ```bash
   pre-commit install
   ```

## Usage

To run the agent, use the `run.py` script:

```bash
python run.py
```

This will execute the agent with a predefined deal ID and print the output.

## Development

- **Code Quality**: The project uses `black`, `flake8`, and `isort` for code formatting and linting. Run `pre-commit run --all-files` to check code quality.
- **Testing**: Use `pytest` to run tests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 