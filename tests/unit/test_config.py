"""
Unit tests for backend/core/config.py - Settings loading.

These tests exercise the load_settings() function using environment variable
injection so they work without a real .env file.
"""

from __future__ import annotations

import pytest


def _minimal_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch only the environment variables required by the application."""
    monkeypatch.setenv("GOOGLE_AI_API_KEY", "test-google-key")
    monkeypatch.setenv("ASTRA_DB_TOKEN", "test-astra-token")
    monkeypatch.setenv(
        "ASTRA_DB_API_ENDPOINT",
        "https://test.astra.datastax.com",
    )

    # watsonx.ai must remain optional.
    monkeypatch.delenv("WX_API_KEY", raising=False)
    monkeypatch.delenv("WX_PROJECT_ID", raising=False)


class TestLoadSettings:
    def test_loads_with_required_vars(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Settings load successfully without watsonx.ai credentials."""
        _minimal_env(monkeypatch)

        import backend.core.config as cfg

        cfg._settings = None
        settings = cfg.load_settings()

        assert settings.google_ai_api_key == "test-google-key"
        assert settings.astra_db_token == "test-astra-token"
        assert (
            settings.astra_db_api_endpoint
            == "https://test.astra.datastax.com"
        )

        # watsonx.ai is optional until IBM Cloud access is available.
        assert settings.wx_api_key == ""
        assert settings.wx_project_id == ""

    def test_loads_optional_watsonx_vars(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Optional watsonx.ai credentials load when provided."""
        _minimal_env(monkeypatch)
        monkeypatch.setenv("WX_API_KEY", "test-wx-key")
        monkeypatch.setenv("WX_PROJECT_ID", "test-wx-project")

        import backend.core.config as cfg

        cfg._settings = None
        settings = cfg.load_settings()

        assert settings.wx_api_key == "test-wx-key"
        assert settings.wx_project_id == "test-wx-project"

    def test_raises_on_missing_required_var(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """EnvironmentError is raised when a required variable is absent."""
        _minimal_env(monkeypatch)
        monkeypatch.delenv("GOOGLE_AI_API_KEY", raising=False)

        import backend.core.config as cfg

        cfg._settings = None

        with pytest.raises(EnvironmentError, match="GOOGLE_AI_API_KEY"):
            cfg.load_settings()

    def test_default_embedding_model(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Embedding model defaults match UD-03."""
        _minimal_env(monkeypatch)

        import backend.core.config as cfg

        cfg._settings = None
        settings = cfg.load_settings()

        assert settings.embedding_model == "gemini-embedding-001"
        assert settings.embedding_dimensions == 3072

    def test_default_retrieval_thresholds(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Retrieval thresholds match UD-02 provisional values."""
        _minimal_env(monkeypatch)

        import backend.core.config as cfg

        cfg._settings = None
        settings = cfg.load_settings()

        assert settings.retrieval_score_refuse == 0.55
        assert settings.retrieval_score_proceed == 0.68
        assert settings.retrieval_top_k == 7

    def test_collection_names_are_locked(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Default collection names must match ARCHITECTURE.md."""
        _minimal_env(monkeypatch)

        import backend.core.config as cfg

        cfg._settings = None
        settings = cfg.load_settings()

        assert settings.kb_collection == "mechacode_guardian_kb"
        assert settings.reports_collection == "diagnosis_reports"