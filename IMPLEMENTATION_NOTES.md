# Sharesight Skill - Implementation Notes

## Overview

OpenClaw skill for the Sharesight API. Uses Python with uv, OAuth 2.0 Client Credentials flow. Supports full CRUD operations for portfolios, holdings, trades, custom investments, prices, and coupon rates.

## Project Structure

```
sharesight-skill/
├── pyproject.toml           # uv/Python project config
├── SKILL.md                 # OpenClaw skill definition
├── README.md                # User documentation
├── IMPLEMENTATION_NOTES.md  # This file
├── .gitignore
├── src/sharesight/
│   ├── __init__.py          # Package metadata
│   ├── __main__.py          # Entry point for `python -m sharesight`
│   ├── auth.py              # OAuth client credentials flow, token storage
│   ├── client.py            # HTTP client with Bearer auth, auto token refresh
│   ├── api.py               # High-level API methods
│   └── cli.py               # argparse CLI commands
└── tests/
    ├── __init__.py
    ├── test_auth.py         # OAuth and token management tests
    ├── test_client.py       # HTTP client and error tests
    └── test_cli.py          # CLI command tests
```

## Key Design Decisions

1. **Minimal dependencies**: Only `httpx` for HTTP. Uses stdlib `argparse` for CLI.
2. **OAuth Client Credentials**: Simpler than authorization_code, suitable for personal use.
3. **Token caching**: Stored in `~/.config/sharesight-cli/config.json` with auto-refresh.
4. **JSON output**: All commands output JSON for easy parsing by agents.
5. **Write protection**: Uses `@requires_write_permission` decorator. Write operations require `SHARESIGHT_ALLOW_WRITES=true`.
6. **Mixed API versions**: Most endpoints use v3 API, trades use v2 API.

## API Coverage

### Portfolios (Read-only) - v3 API

| Endpoint | Method | CLI Command |
|----------|--------|-------------|
| `/portfolios` | GET | `portfolios list` |
| `/portfolios/{id}` | GET | `portfolios get <id>` |
| `/portfolios/{id}/holdings` | GET | `portfolios holdings <id>` |
| `/portfolios/{id}/performance` | GET | `portfolios performance <id>` |
| `/portfolios/{id}/performance_index_chart` | GET | `portfolios chart <id>` |

### Holdings (Read/Update/Delete) - v3 API

| Endpoint | Method | CLI Command |
|----------|--------|-------------|
| `/holdings` | GET | `holdings list` |
| `/holdings/{id}` | GET | `holdings get <id>` |
| `/holdings/{id}` | PUT | `holdings update <id>` |
| `/holdings/{id}` | DELETE | `holdings delete <id>` |

### Trades (Full CRUD) - v2 API

| Endpoint | Method | CLI Command |
|----------|--------|-------------|
| `/trades.json` | POST | `trades create <portfolio_id>` |
| `/trades/{id}.json` | GET | `trades get <id>` |
| `/trades/{id}.json` | PUT | `trades update <id>` |
| `/trades/{id}.json` | DELETE | `trades delete <id>` |

### Custom Investments (Full CRUD) - v3 API

| Endpoint | Method | CLI Command |
|----------|--------|-------------|
| `/custom_investments` | GET | `investments list` |
| `/custom_investments/{id}` | GET | `investments get <id>` |
| `/custom_investments` | POST | `investments create` |
| `/custom_investments/{id}` | PUT | `investments update <id>` |
| `/custom_investments/{id}` | DELETE | `investments delete <id>` |

### Custom Investment Prices (Full CRUD) - v3 API

| Endpoint | Method | CLI Command |
|----------|--------|-------------|
| `/custom_investment/{id}/prices.json` | GET | `prices list <id>` |
| `/custom_investment/{id}/prices.json` | POST | `prices create <id>` |
| `/prices/{id}.json` | PUT | `prices update <id>` |
| `/prices/{id}.json` | DELETE | `prices delete <id>` |

### Coupon Rates (Full CRUD) - v3 API

| Endpoint | Method | CLI Command |
|----------|--------|-------------|
| `/custom_investments/{id}/coupon_rates` | GET | `coupon-rates list <id>` |
| `/custom_investments/{id}/coupon_rates` | POST | `coupon-rates create <id>` |
| `/coupon_rates/{id}` | PUT | `coupon-rates update <id>` |
| `/coupon_rates/{id}` | DELETE | `coupon-rates delete <id>` |

### Reference Data - v3 API

| Endpoint | Method | CLI Command |
|----------|--------|-------------|
| `/countries` | GET | `countries` |

## Implementation Checklist

- [x] Project setup (pyproject.toml, directory structure)
- [x] Auth module (client credentials flow, token storage)
- [x] HTTP client (GET, POST, PUT, DELETE methods)
- [x] HTTP client (v2 API support for trades)
- [x] API module (portfolio, holdings read endpoints)
- [x] API module (holdings update/delete)
- [x] API module (trades CRUD via v2 API)
- [x] API module (custom investments CRUD)
- [x] API module (prices CRUD)
- [x] API module (coupon rates CRUD)
- [x] CLI module (read commands)
- [x] CLI module (write commands with `@requires_write_permission` decorator)
- [x] Write protection (`SHARESIGHT_ALLOW_WRITES` env var)
- [x] SKILL.md (OpenClaw skill definition)
- [x] README.md (user documentation with OpenClaw install instructions)
- [x] Test suite (64 tests passing)

## Installation

```bash
# Clone into skills directory
cd ~/.claude/skills
git clone https://github.com/your-username/sharesight-skill.git sharesight
cd sharesight && uv sync
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SHARESIGHT_CLIENT_ID` | Yes | API client ID |
| `SHARESIGHT_CLIENT_SECRET` | Yes | API client secret |
| `SHARESIGHT_ALLOW_WRITES` | No | Set to `true` to enable write operations |

For OpenClaw, configure in `~/.openclaw/.env` or `~/.openclaw/openclaw.json`.
See [OpenClaw Environment Configuration](https://docs.openclaw.ai/environment).

## Testing

```bash
# Install with dev dependencies
cd sharesight-skill && uv sync --extra dev

# Run test suite (64 tests)
uv run pytest tests/ -v

# Verify CLI loads
uv run sharesight --help

# Test auth (requires credentials)
export SHARESIGHT_CLIENT_ID="..."
export SHARESIGHT_CLIENT_SECRET="..."
uv run sharesight auth login
uv run sharesight portfolios list
```

### Test Coverage

| File | Tests | Coverage |
|------|-------|----------|
| `tests/test_auth.py` | 15 | OAuth credentials, token caching, refresh, expiry |
| `tests/test_client.py` | 13 | HTTP requests, error handling, 401 retry, PUT/DELETE |
| `tests/test_cli.py` | 36 | Argument parsing, CLI commands, write protection |

## Notes

- Sharesight access tokens expire after 30 minutes
- API is in closed beta - contact Sharesight for access
- Base URLs:
  - v3 API: `https://api.sharesight.com/api/v3/`
  - v2 API: `https://api.sharesight.com/api/v2/` (trades only)
- Trades API uses different field names (`transaction_date` vs `trade_date`)
