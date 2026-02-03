"""Tests for auth module."""

import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest

from sharesight import auth


@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    """Use a temporary config directory for tests."""
    config_dir = tmp_path / ".config" / "sharesight-cli"
    monkeypatch.setattr(auth, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(auth, "CONFIG_FILE", config_dir / "config.json")
    return config_dir


@pytest.fixture
def mock_credentials(monkeypatch):
    """Set mock credentials in environment."""
    monkeypatch.setenv("SHARESIGHT_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("SHARESIGHT_CLIENT_SECRET", "test_client_secret")


class TestGetCredentials:
    def test_get_credentials_success(self, mock_credentials):
        client_id, client_secret = auth.get_credentials()
        assert client_id == "test_client_id"
        assert client_secret == "test_client_secret"

    def test_get_credentials_missing_client_id(self, monkeypatch):
        monkeypatch.delenv("SHARESIGHT_CLIENT_ID", raising=False)
        monkeypatch.delenv("SHARESIGHT_CLIENT_SECRET", raising=False)
        with pytest.raises(ValueError, match="Missing credentials"):
            auth.get_credentials()

    def test_get_credentials_missing_client_secret(self, monkeypatch):
        monkeypatch.setenv("SHARESIGHT_CLIENT_ID", "test_id")
        monkeypatch.delenv("SHARESIGHT_CLIENT_SECRET", raising=False)
        with pytest.raises(ValueError, match="Missing credentials"):
            auth.get_credentials()


class TestConfigStorage:
    def test_load_config_empty(self, temp_config_dir):
        config = auth.load_config()
        assert config == {}

    def test_save_and_load_config(self, temp_config_dir):
        test_config = {"access_token": "test_token", "expires_at": 12345}
        auth.save_config(test_config)

        loaded = auth.load_config()
        assert loaded == test_config

    def test_save_config_creates_directory(self, temp_config_dir):
        assert not temp_config_dir.exists()
        auth.save_config({"test": "value"})
        assert temp_config_dir.exists()


class TestGetToken:
    def test_get_token_returns_cached_valid_token(self, temp_config_dir, mock_credentials):
        # Save a valid token
        auth.save_config({
            "access_token": "cached_token",
            "expires_at": time.time() + 3600,  # Valid for 1 hour
        })

        token = auth.get_token()
        assert token == "cached_token"

    def test_get_token_refreshes_expired_token(self, temp_config_dir, mock_credentials, httpx_mock):
        # Save an expired token
        auth.save_config({
            "access_token": "old_token",
            "expires_at": time.time() - 100,  # Expired
        })

        httpx_mock.add_response(
            method="POST",
            url=auth.TOKEN_URL,
            json={
                "access_token": "new_token",
                "expires_in": 1800,
                "token_type": "Bearer",
            },
        )

        token = auth.get_token()
        assert token == "new_token"

    def test_get_token_force_refresh(self, temp_config_dir, mock_credentials, httpx_mock):
        # Save a valid token
        auth.save_config({
            "access_token": "cached_token",
            "expires_at": time.time() + 3600,
        })

        httpx_mock.add_response(
            method="POST",
            url=auth.TOKEN_URL,
            json={
                "access_token": "fresh_token",
                "expires_in": 1800,
                "token_type": "Bearer",
            },
        )

        token = auth.get_token(force_refresh=True)
        assert token == "fresh_token"

    def test_get_token_api_error(self, temp_config_dir, mock_credentials, httpx_mock):
        httpx_mock.add_response(
            method="POST",
            url=auth.TOKEN_URL,
            status_code=401,
            text="Invalid credentials",
        )

        with pytest.raises(ValueError, match="Failed to get access token"):
            auth.get_token()


class TestClearToken:
    def test_clear_token(self, temp_config_dir):
        auth.save_config({
            "access_token": "test_token",
            "expires_at": 12345,
            "token_type": "Bearer",
            "other_field": "preserved",
        })

        auth.clear_token()

        config = auth.load_config()
        assert "access_token" not in config
        assert "expires_at" not in config
        assert "token_type" not in config
        assert config.get("other_field") == "preserved"


class TestIsAuthenticated:
    def test_is_authenticated_true(self, temp_config_dir, mock_credentials):
        auth.save_config({
            "access_token": "valid_token",
            "expires_at": time.time() + 3600,
        })

        assert auth.is_authenticated() is True

    def test_is_authenticated_expired(self, temp_config_dir, mock_credentials):
        auth.save_config({
            "access_token": "expired_token",
            "expires_at": time.time() - 100,
        })

        assert auth.is_authenticated() is False

    def test_is_authenticated_no_token(self, temp_config_dir, mock_credentials):
        assert auth.is_authenticated() is False

    def test_is_authenticated_no_credentials(self, temp_config_dir, monkeypatch):
        monkeypatch.delenv("SHARESIGHT_CLIENT_ID", raising=False)
        monkeypatch.delenv("SHARESIGHT_CLIENT_SECRET", raising=False)
        assert auth.is_authenticated() is False
