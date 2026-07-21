"""
Core configuration for MechaCode Guardian backend.

Loads all required environment variables at startup. Missing required variables
raise a clear error so the developer knows exactly what is needed.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    """Validated application settings loaded from environment variables."""

    # --- Required fields first (no defaults) ---

    # Google AI (embeddings + Gemini fallback LLM)
    google_ai_api_key: str

    # watsonx.ai (IBM Granite primary LLM)
    wx_api_key: str
    wx_project_id: str

    # Astra DB (vector store)
    astra_db_token: str
    astra_db_api_endpoint: str

    # --- Optional fields with defaults ---

    wx_url: str = "https://us-south.ml.cloud.ibm.com"
    astra_db_keyspace: str = "default_keyspace"

    # Collection names (do NOT modify — matches ARCHITECTURE.md)
    kb_collection: str = "mechacode_guardian_kb"
    reports_collection: str = "diagnosis_reports"

    # Embedding config (UD-03 — must not be changed without re-ingesting all docs)
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 3072

    # Retrieval policy thresholds (UD-02 — provisional, calibrate on Day 9)
    retrieval_score_refuse: float = 0.55   # below this → SR-06 refusal
    retrieval_score_proceed: float = 0.68  # at or above this → proceed normally
    retrieval_top_k: int = 7

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:5173"])


def load_settings() -> Settings:
    """
    Load and validate settings from environment variables.

    Raises:
        EnvironmentError: If any required variable is absent or empty.
    """

    def _require(name: str) -> str:
        value = os.environ.get(name, "").strip()
        if not value:
            raise EnvironmentError(
                f"Required environment variable '{name}' is not set. "
                "Copy .env.example to .env and fill in the values."
            )
        return value

    def _optional(name: str, default: str = "") -> str:
        return os.environ.get(name, default).strip() or default

    return Settings(
        google_ai_api_key=_require("GOOGLE_AI_API_KEY"),
        wx_api_key=_require("WX_API_KEY"),
        wx_project_id=_require("WX_PROJECT_ID"),
        wx_url=_optional("WX_URL", "https://us-south.ml.cloud.ibm.com"),
        astra_db_token=_require("ASTRA_DB_TOKEN"),
        astra_db_api_endpoint=_require("ASTRA_DB_API_ENDPOINT"),
        astra_db_keyspace=_optional("ASTRA_DB_KEYSPACE", "default_keyspace"),
        kb_collection=_optional("KB_COLLECTION", "mechacode_guardian_kb"),
        reports_collection=_optional("REPORTS_COLLECTION", "diagnosis_reports"),
        environment=_optional("ENVIRONMENT", "development"),
        log_level=_optional("LOG_LEVEL", "INFO"),
        cors_origins=[
            o.strip()
            for o in _optional("CORS_ORIGINS", "http://localhost:5173").split(",")
            if o.strip()
        ],
    )


# Module-level singleton — populated when the app starts via get_settings().
_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the cached settings singleton, loading from env if not yet loaded."""
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings
