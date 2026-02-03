"""Tests for CLI module."""

import json
import sys
import time
from io import StringIO
from unittest.mock import patch, MagicMock

import pytest

from sharesight import auth
from sharesight.cli import main, create_parser, WritesDisabledError, requires_write_permission


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


class TestParser:
    def test_parser_creation(self):
        parser = create_parser()
        assert parser is not None

    def test_parser_help(self):
        parser = create_parser()
        # Just verify it doesn't raise
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--help"])
        assert exc_info.value.code == 0

    def test_parser_version(self):
        parser = create_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        assert exc_info.value.code == 0

    def test_parser_portfolios_list(self):
        parser = create_parser()
        args = parser.parse_args(["portfolios", "list"])
        assert args.command == "portfolios"
        assert args.portfolios_command == "list"

    def test_parser_portfolios_get(self):
        parser = create_parser()
        args = parser.parse_args(["portfolios", "get", "123"])
        assert args.command == "portfolios"
        assert args.portfolios_command == "get"
        assert args.id == 123

    def test_parser_portfolios_performance(self):
        parser = create_parser()
        args = parser.parse_args([
            "portfolios", "performance", "123",
            "--start-date", "2024-01-01",
            "--end-date", "2024-12-31",
            "--grouping", "market",
        ])
        assert args.command == "portfolios"
        assert args.portfolios_command == "performance"
        assert args.id == 123
        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-12-31"
        assert args.grouping == "market"

    def test_parser_holdings_list(self):
        parser = create_parser()
        args = parser.parse_args(["holdings", "list"])
        assert args.command == "holdings"
        assert args.holdings_command == "list"

    def test_parser_holdings_get(self):
        parser = create_parser()
        args = parser.parse_args(["holdings", "get", "456", "--avg-price", "--cost-base"])
        assert args.command == "holdings"
        assert args.holdings_command == "get"
        assert args.id == 456
        assert args.avg_price is True
        assert args.cost_base is True

    def test_parser_countries(self):
        parser = create_parser()
        args = parser.parse_args(["countries", "--supported"])
        assert args.command == "countries"
        assert args.supported is True

    def test_parser_auth_login(self):
        parser = create_parser()
        args = parser.parse_args(["auth", "login"])
        assert args.command == "auth"
        assert args.auth_command == "login"

    def test_parser_auth_status(self):
        parser = create_parser()
        args = parser.parse_args(["auth", "status"])
        assert args.command == "auth"
        assert args.auth_command == "status"

    def test_parser_holdings_update(self):
        parser = create_parser()
        args = parser.parse_args(["holdings", "update", "123", "--enable-drp", "true", "--drp-mode", "up"])
        assert args.command == "holdings"
        assert args.holdings_command == "update"
        assert args.id == 123
        assert args.enable_drp is True
        assert args.drp_mode == "up"

    def test_parser_holdings_delete(self):
        parser = create_parser()
        args = parser.parse_args(["holdings", "delete", "123"])
        assert args.command == "holdings"
        assert args.holdings_command == "delete"
        assert args.id == 123

    def test_parser_investments_list(self):
        parser = create_parser()
        args = parser.parse_args(["investments", "list", "--portfolio-id", "456"])
        assert args.command == "investments"
        assert args.investments_command == "list"
        assert args.portfolio_id == 456

    def test_parser_investments_create(self):
        parser = create_parser()
        args = parser.parse_args([
            "investments", "create",
            "--code", "TEST",
            "--name", "Test Investment",
            "--country", "AU",
            "--type", "ORDINARY",
        ])
        assert args.command == "investments"
        assert args.investments_command == "create"
        assert args.code == "TEST"
        assert args.name == "Test Investment"
        assert args.country == "AU"
        assert args.type == "ORDINARY"

    def test_parser_prices_list(self):
        parser = create_parser()
        args = parser.parse_args(["prices", "list", "123", "--start-date", "2024-01-01"])
        assert args.command == "prices"
        assert args.prices_command == "list"
        assert args.instrument_id == 123
        assert args.start_date == "2024-01-01"

    def test_parser_prices_create(self):
        parser = create_parser()
        args = parser.parse_args(["prices", "create", "123", "--price", "100.50", "--date", "2024-01-01"])
        assert args.command == "prices"
        assert args.prices_command == "create"
        assert args.instrument_id == 123
        assert args.price == 100.50
        assert args.date == "2024-01-01"

    def test_parser_coupon_rates_list(self):
        parser = create_parser()
        args = parser.parse_args(["coupon-rates", "list", "123"])
        assert args.command == "coupon-rates"
        assert args.coupon_command == "list"
        assert args.instrument_id == 123

    def test_parser_coupon_rates_create(self):
        parser = create_parser()
        args = parser.parse_args(["coupon-rates", "create", "123", "--rate", "5.5", "--date", "2024-01-01"])
        assert args.command == "coupon-rates"
        assert args.coupon_command == "create"
        assert args.instrument_id == 123
        assert args.rate == 5.5
        assert args.date == "2024-01-01"


class TestMainAuth:
    def test_auth_login_success(self, temp_config_dir, mock_credentials, httpx_mock, capsys):
        httpx_mock.add_response(
            method="POST",
            url=auth.TOKEN_URL,
            json={
                "access_token": "new_token",
                "expires_in": 1800,
                "token_type": "Bearer",
            },
        )

        with patch.object(sys, "argv", ["sharesight", "auth", "login"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["status"] == "authenticated"

    def test_auth_status_authenticated(self, temp_config_dir, mock_credentials, valid_token, capsys):
        with patch.object(sys, "argv", ["sharesight", "auth", "status"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["authenticated"] is True

    def test_auth_status_not_authenticated(self, temp_config_dir, mock_credentials, capsys):
        with patch.object(sys, "argv", ["sharesight", "auth", "status"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["authenticated"] is False

    def test_auth_clear(self, temp_config_dir, valid_token, capsys):
        with patch.object(sys, "argv", ["sharesight", "auth", "clear"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["status"] == "success"

        # Verify token was cleared
        config = auth.load_config()
        assert "access_token" not in config


class TestMainPortfolios:
    def test_portfolios_list(self, mock_credentials, valid_token, httpx_mock, capsys):
        httpx_mock.add_response(
            method="GET",
            url="https://api.sharesight.com/api/v3/portfolios",
            json={"portfolios": [{"id": 1, "name": "Test"}]},
        )

        with patch.object(sys, "argv", ["sharesight", "portfolios", "list"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "portfolios" in output

    def test_portfolios_get(self, mock_credentials, valid_token, httpx_mock, capsys):
        httpx_mock.add_response(
            method="GET",
            url="https://api.sharesight.com/api/v3/portfolios/123",
            json={"portfolio": {"id": 123, "name": "My Portfolio"}},
        )

        with patch.object(sys, "argv", ["sharesight", "portfolios", "get", "123"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["portfolio"]["id"] == 123


class TestMainHoldings:
    def test_holdings_list(self, mock_credentials, valid_token, httpx_mock, capsys):
        httpx_mock.add_response(
            method="GET",
            url="https://api.sharesight.com/api/v3/holdings",
            json={"holdings": [{"id": 1, "symbol": "AAPL"}]},
        )

        with patch.object(sys, "argv", ["sharesight", "holdings", "list"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "holdings" in output


class TestMainCountries:
    def test_countries_list(self, mock_credentials, valid_token, httpx_mock, capsys):
        httpx_mock.add_response(
            method="GET",
            url="https://api.sharesight.com/api/v3/countries",
            json={"countries": [{"code": "AU", "name": "Australia"}]},
        )

        with patch.object(sys, "argv", ["sharesight", "countries"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "countries" in output


class TestMainErrors:
    def test_api_error_handling(self, mock_credentials, valid_token, httpx_mock, capsys):
        httpx_mock.add_response(
            method="GET",
            url="https://api.sharesight.com/api/v3/portfolios",
            status_code=403,
            json={"error": "forbidden", "reason": "Access denied"},
        )

        with patch.object(sys, "argv", ["sharesight", "portfolios", "list"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error_output = json.loads(captured.err)
        assert "error" in error_output

    def test_no_command_shows_help(self, capsys):
        with patch.object(sys, "argv", ["sharesight"]):
            result = main()

        assert result == 0
        # Help output goes to stdout
        captured = capsys.readouterr()
        assert "usage:" in captured.out or "Available commands" in captured.out


class TestWriteProtection:
    def test_decorator_raises_when_not_set(self, monkeypatch):
        monkeypatch.delenv("SHARESIGHT_ALLOW_WRITES", raising=False)

        @requires_write_permission
        def dummy_write():
            return "success"

        with pytest.raises(WritesDisabledError) as exc_info:
            dummy_write()
        assert "SHARESIGHT_ALLOW_WRITES=true" in str(exc_info.value)

    def test_decorator_raises_when_false(self, monkeypatch):
        monkeypatch.setenv("SHARESIGHT_ALLOW_WRITES", "false")

        @requires_write_permission
        def dummy_write():
            return "success"

        with pytest.raises(WritesDisabledError):
            dummy_write()

    def test_decorator_allows_when_true(self, monkeypatch):
        monkeypatch.setenv("SHARESIGHT_ALLOW_WRITES", "true")

        @requires_write_permission
        def dummy_write():
            return "success"

        assert dummy_write() == "success"

    def test_decorator_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("SHARESIGHT_ALLOW_WRITES", "TRUE")

        @requires_write_permission
        def dummy_write():
            return "success"

        assert dummy_write() == "success"

    def test_holdings_update_blocked_without_permission(self, mock_credentials, valid_token, capsys, monkeypatch):
        monkeypatch.delenv("SHARESIGHT_ALLOW_WRITES", raising=False)
        with patch.object(sys, "argv", ["sharesight", "holdings", "update", "123", "--enable-drp", "true"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error_output = json.loads(captured.err)
        assert "SHARESIGHT_ALLOW_WRITES" in error_output["error"]
        assert error_output["hint"] == "export SHARESIGHT_ALLOW_WRITES=true"

    def test_holdings_delete_blocked_without_permission(self, mock_credentials, valid_token, capsys, monkeypatch):
        monkeypatch.delenv("SHARESIGHT_ALLOW_WRITES", raising=False)
        with patch.object(sys, "argv", ["sharesight", "holdings", "delete", "123"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error_output = json.loads(captured.err)
        assert "SHARESIGHT_ALLOW_WRITES" in error_output["error"]

    def test_investments_create_blocked_without_permission(self, mock_credentials, valid_token, capsys, monkeypatch):
        monkeypatch.delenv("SHARESIGHT_ALLOW_WRITES", raising=False)
        with patch.object(sys, "argv", ["sharesight", "investments", "create", "--code", "TEST", "--name", "Test", "--country", "AU", "--type", "ORDINARY"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        error_output = json.loads(captured.err)
        assert "SHARESIGHT_ALLOW_WRITES" in error_output["error"]

    def test_write_allowed_with_env_var(self, mock_credentials, valid_token, httpx_mock, capsys, monkeypatch):
        monkeypatch.setenv("SHARESIGHT_ALLOW_WRITES", "true")
        httpx_mock.add_response(
            method="DELETE",
            url="https://api.sharesight.com/api/v3/holdings/123",
            json={"deleted": True},
        )

        with patch.object(sys, "argv", ["sharesight", "holdings", "delete", "123"]):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["deleted"] is True
