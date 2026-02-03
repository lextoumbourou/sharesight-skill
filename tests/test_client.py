"""Tests for client module."""

import time
from unittest.mock import patch, MagicMock

import httpx
import pytest

from sharesight import auth
from sharesight.client import SharesightClient, APIError


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


@pytest.fixture
def valid_token(temp_config_dir):
    """Set up a valid cached token."""
    auth.save_config({
        "access_token": "test_access_token",
        "expires_at": time.time() + 3600,
        "token_type": "Bearer",
    })


class TestSharesightClient:
    def test_get_request_success(self, mock_credentials, valid_token, httpx_mock):
        httpx_mock.add_response(
            method="GET",
            url="https://api.sharesight.com/api/v3/portfolios",
            json={"portfolios": [{"id": 1, "name": "Test"}]},
        )

        client = SharesightClient()
        result = client.get("/portfolios")

        assert result == {"portfolios": [{"id": 1, "name": "Test"}]}
        client.close()

    def test_get_request_with_params(self, mock_credentials, valid_token, httpx_mock):
        httpx_mock.add_response(
            method="GET",
            url="https://api.sharesight.com/api/v3/portfolios?consolidated=true",
            json={"portfolios": []},
        )

        client = SharesightClient()
        result = client.get("/portfolios", params={"consolidated": "true"})

        assert result == {"portfolios": []}
        client.close()

    def test_post_request_success(self, mock_credentials, valid_token, httpx_mock):
        httpx_mock.add_response(
            method="POST",
            url="https://api.sharesight.com/api/v3/test",
            json={"success": True},
        )

        client = SharesightClient()
        result = client.post("/test", json_data={"key": "value"})

        assert result == {"success": True}
        client.close()

    def test_put_request_success(self, mock_credentials, valid_token, httpx_mock):
        httpx_mock.add_response(
            method="PUT",
            url="https://api.sharesight.com/api/v3/holdings/123",
            json={"holding": {"id": 123, "drp_mode_setting": "up"}},
        )

        client = SharesightClient()
        result = client.put("/holdings/123", json_data={"enable_drp": True})

        assert result == {"holding": {"id": 123, "drp_mode_setting": "up"}}
        client.close()

    def test_delete_request_success(self, mock_credentials, valid_token, httpx_mock):
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.sharesight.com/api/v3/holdings/123",
            json={"deleted": True},
        )

        client = SharesightClient()
        result = client.delete("/holdings/123")

        assert result == {"deleted": True}
        client.close()

    def test_context_manager(self, mock_credentials, valid_token, httpx_mock):
        httpx_mock.add_response(
            method="GET",
            url="https://api.sharesight.com/api/v3/portfolios",
            json={"portfolios": []},
        )

        with SharesightClient() as client:
            result = client.get("/portfolios")
            assert result == {"portfolios": []}

    def test_api_error_with_reason(self, mock_credentials, valid_token, httpx_mock):
        httpx_mock.add_response(
            method="GET",
            url="https://api.sharesight.com/api/v3/portfolios/999",
            status_code=404,
            json={"error": "not_found", "reason": "Portfolio not found"},
        )

        client = SharesightClient()
        with pytest.raises(APIError) as exc_info:
            client.get("/portfolios/999")

        assert exc_info.value.status_code == 404
        assert "Portfolio not found" in exc_info.value.message
        client.close()

    def test_api_error_with_error_field(self, mock_credentials, valid_token, httpx_mock):
        httpx_mock.add_response(
            method="GET",
            url="https://api.sharesight.com/api/v3/test",
            status_code=400,
            json={"error": "Bad request"},
        )

        client = SharesightClient()
        with pytest.raises(APIError) as exc_info:
            client.get("/test")

        assert exc_info.value.status_code == 400
        assert "Bad request" in exc_info.value.message
        client.close()

    def test_api_error_plain_text(self, mock_credentials, valid_token, httpx_mock):
        httpx_mock.add_response(
            method="GET",
            url="https://api.sharesight.com/api/v3/test",
            status_code=500,
            text="Internal Server Error",
        )

        client = SharesightClient()
        with pytest.raises(APIError) as exc_info:
            client.get("/test")

        assert exc_info.value.status_code == 500
        assert "Internal Server Error" in exc_info.value.message
        client.close()

    def test_401_triggers_token_refresh(self, temp_config_dir, mock_credentials, httpx_mock):
        # Start with an expired token that will be refreshed
        auth.save_config({
            "access_token": "old_token",
            "expires_at": time.time() + 3600,  # Looks valid but server rejects it
        })

        # First request returns 401
        httpx_mock.add_response(
            method="GET",
            url="https://api.sharesight.com/api/v3/portfolios",
            status_code=401,
            json={"Reason": "Token expired"},
        )

        # Token refresh succeeds
        httpx_mock.add_response(
            method="POST",
            url=auth.TOKEN_URL,
            json={
                "access_token": "new_token",
                "expires_in": 1800,
                "token_type": "Bearer",
            },
        )

        # Retry with new token succeeds
        httpx_mock.add_response(
            method="GET",
            url="https://api.sharesight.com/api/v3/portfolios",
            json={"portfolios": []},
        )

        client = SharesightClient()
        result = client.get("/portfolios")

        assert result == {"portfolios": []}
        client.close()


class TestAPIError:
    def test_api_error_str(self):
        error = APIError(404, "Not found")
        assert str(error) == "API Error 404: Not found"

    def test_api_error_attributes(self):
        error = APIError(500, "Server error")
        assert error.status_code == 500
        assert error.message == "Server error"
