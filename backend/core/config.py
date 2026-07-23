"""
Core configuration for MechaCode Guardian backend.

Loads all required environment variables at startup. Missing required variables
raise a clear error so the developer knows exactly what is needed.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


# Project-root environment file:
# mechacode-guardian/.env
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


@dataclass(frozen=True)
class Settings:
    """Validated application settings loaded from environment variables."""

    # Required configuration

    # Google AI (embeddings and temporary primary LLM)
    google_ai_api_key: str

    # Astra DB (vector store)
    astra_db_token: str
    astra_db_api_endpoint: str

    # Optional watsonx.ai configuration
    # Leave these empty until IBM Cloud access is available.
    wx_api_key: str = ""
    wx_project_id: str = ""
    wx_url: str = "https://us-south.ml.cloud.ibm.com"

    # Astra DB namespace
    astra_db_keyspace: str = "default_keyspace"

    # Collection names (must match ARCHITECTURE.md)
    kb_collection: str = "mechacode_guardian_kb"
    reports_collection: str = "diagnosis_reports"

    # Embedding configuration (UD-03)
    # Changing these values requires re-ingesting all documents.
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 3072

    # Retrieval policy thresholds (UD-02)
    retrieval_score_refuse: float = 0.55
    retrieval_score_proceed: float = 0.68
    retrieval_top_k: int = 7

    # Application configuration
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = field(
        default_factory=lambda: ["http://localhost:5173"]
    )


def load_settings() -> Settings:
    """
    Load and validate settings from environment variables.

    Existing system environment variables take precedence over values
    declared in the project-root .env file.

    Raises:
        EnvironmentError: If any required environment variable is absent
            or empty.
    """
    load_dotenv(dotenv_path=_ENV_FILE, override=False)

    def _require(name: str) -> str:
        value = os.environ.get(name, "").strip()

        if not value:
            raise EnvironmentError(
                f"Required environment variable '{name}' is not set. "
                "Copy .env.example to .env and fill in the values."
            )

        return value

    def _optional(name: str, default: str = "") -> str:
        value = os.environ.get(name, default).strip()
        return value or default

    return Settings(
        google_ai_api_key=_require("GOOGLE_AI_API_KEY"),
        astra_db_token=_require("ASTRA_DB_TOKEN"),
        astra_db_api_endpoint=_require("ASTRA_DB_API_ENDPOINT"),
        wx_api_key=_optional("WX_API_KEY"),
        wx_project_id=_optional("WX_PROJECT_ID"),
        wx_url=_optional(
            "WX_URL",
            "https://us-south.ml.cloud.ibm.com",
        ),
        astra_db_keyspace=_optional(
            "ASTRA_DB_KEYSPACE",
            "default_keyspace",
        ),
        kb_collection=_optional(
            "KB_COLLECTION",
            "mechacode_guardian_kb",
        ),
        reports_collection=_optional(
            "REPORTS_COLLECTION",
            "diagnosis_reports",
        ),
        environment=_optional(
            "ENVIRONMENT",
            "development",
        ),
        log_level=_optional(
            "LOG_LEVEL",
            "INFO",
        ),
        cors_origins=[
            origin.strip()
            for origin in _optional(
                "CORS_ORIGINS",
                "http://localhost:5173",
            ).split(",")
            if origin.strip()
        ],
    )


# Module-level singleton populated when get_settings() is first called.
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Return the cached application settings.

    Settings are loaded from environment variables on the first call.
    """
    global _settings

    if _settings is None:
        _settings = load_settings()

    return _settings