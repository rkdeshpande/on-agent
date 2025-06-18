"""
Centralized configuration management for the Offer Negotiation Agent.
Makes all file paths and environment variables configurable.
"""

import os
from pathlib import Path
from typing import Optional


class AppConfig:
    """Centralized configuration for the application."""

    def __init__(self):
        # Base paths - can be overridden by environment variables
        self._base_dir = Path(os.getenv("APP_BASE_DIR", "."))
        self._config_dir = Path(os.getenv("CONFIG_DIR", self._base_dir / "config"))
        self._data_dir = Path(os.getenv("DATA_DIR", self._base_dir / "data"))
        self._logs_dir = Path(os.getenv("LOGS_DIR", self._base_dir / "logs"))

        # Ensure directories exist
        self._logs_dir.mkdir(exist_ok=True)

    @property
    def base_dir(self) -> Path:
        """Base directory of the application."""
        return self._base_dir

    @property
    def config_dir(self) -> Path:
        """Configuration directory."""
        return self._config_dir

    @property
    def data_dir(self) -> Path:
        """Data directory."""
        return self._data_dir

    @property
    def logs_dir(self) -> Path:
        """Logs directory."""
        return self._logs_dir

    # File paths
    @property
    def secrets_env_path(self) -> Path:
        """Path to secrets environment file."""
        return self._config_dir / "secrets.env"

    @property
    def model_settings_path(self) -> Path:
        """Path to model settings YAML file."""
        return self._config_dir / "model_settings.yaml"

    @property
    def prompts_dir(self) -> Path:
        """Path to prompts directory."""
        return self._config_dir / "prompts"

    @property
    def deals_dir(self) -> Path:
        """Path to deals data directory."""
        return self._data_dir / "deals"

    @property
    def domain_knowledge_dir(self) -> Path:
        """Path to domain knowledge directory."""
        return self._data_dir / "domain_knowledge"

    @property
    def log_file_path(self) -> Path:
        """Path to the main log file."""
        return self._logs_dir / "agent.log"

    # Environment variables with defaults
    @property
    def openai_api_key(self) -> Optional[str]:
        """OpenAI API key."""
        return os.getenv("OPENAI_API_KEY")

    @property
    def submission_dir(self) -> Optional[str]:
        """External submission directory."""
        return os.getenv("SUBMISSION_DIR")

    @property
    def langchain_tracing_v2(self) -> bool:
        """Whether to enable LangChain tracing v2."""
        return os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"

    @property
    def langchain_api_key(self) -> Optional[str]:
        """LangChain API key."""
        return os.getenv("LANGCHAIN_API_KEY")

    @property
    def langchain_endpoint(self) -> str:
        """LangChain endpoint URL."""
        return os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

    @property
    def langchain_project(self) -> str:
        """LangChain project name."""
        return os.getenv("LANGCHAIN_PROJECT", "OfferNegotiationAgent")

    def validate(self) -> bool:
        """Validate that required configuration is present."""
        errors = []

        # Check required files exist
        if not self.secrets_env_path.exists():
            errors.append(f"Secrets file not found: {self.secrets_env_path}")

        if not self.model_settings_path.exists():
            errors.append(f"Model settings file not found: {self.model_settings_path}")

        if not self.prompts_dir.exists():
            errors.append(f"Prompts directory not found: {self.prompts_dir}")

        if not self.deals_dir.exists():
            errors.append(f"Deals directory not found: {self.deals_dir}")

        if not self.domain_knowledge_dir.exists():
            errors.append(
                f"Domain knowledge directory not found: {self.domain_knowledge_dir}"
            )

        # Check required environment variables
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY environment variable not set")

        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")  # noqa: E221
            return False

        return True


# Global configuration instance
config = AppConfig()
