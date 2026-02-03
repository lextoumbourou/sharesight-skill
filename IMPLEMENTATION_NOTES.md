# Sharesight Skill - Implementation Notes

## Overview

OpenClaw skill for the Sharesight API. Uses Python with uv, OAuth 2.0 Client Credentials flow. Supports full CRUD operations for portfolios, holdings, custom investments, prices, and coupon rates.

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
5. **Write protection**: Write operations (create, update, delete) require `SHARESIGHT_ALLOW_WRITES=true` for safety.

## API Coverage

### Portfolios (Read-only)

| Endpoint | Method | CLI Command |
|----------|--------|-------------|
| `/portfolios` | GET | `portfolios list` |
| `/portfolios/{id}` | GET | `portfolios get <id>` |
| `/portfolios/{id}/holdings` | GET | `portfolios holdings <id>` |
| `/portfolios/{id}/performance` | GET | `portfolios performance <id>` |
| `/portfolios/{id}/performance_index_chart` | GET | `portfolios chart <id>` |

### Holdings (Read/Update/Delete)

| Endpoint | Method | CLI Command |
|----------|--------|-------------|
| `/holdings` | GET | `holdings list` |
| `/holdings/{id}` | GET | `holdings get <id>` |
| `/holdings/{id}` | PUT | `holdings update <id>` |
| `/holdings/{id}` | DELETE | `holdings delete <id>` |

### Custom Investments (Full CRUD)

| Endpoint | Method | CLI Command |
|----------|--------|-------------|
| `/custom_investments` | GET | `investments list` |
| `/custom_investments/{id}` | GET | `investments get <id>` |
| `/custom_investments` | POST | `investments create` |
| `/custom_investments/{id}` | PUT | `investments update <id>` |
| `/custom_investments/{id}` | DELETE | `investments delete <id>` |

### Custom Investment Prices (Full CRUD)

| Endpoint | Method | CLI Command |
|----------|--------|-------------|
| `/custom_investment/{id}/prices.json` | GET | `prices list <id>` |
| `/custom_investment/{id}/prices.json` | POST | `prices create <id>` |
| `/prices/{id}.json` | PUT | `prices update <id>` |
| `/prices/{id}.json` | DELETE | `prices delete <id>` |

### Coupon Rates (Full CRUD)

| Endpoint | Method | CLI Command |
|----------|--------|-------------|
| `/custom_investments/{id}/coupon_rates` | GET | `coupon-rates list <id>` |
| `/custom_investments/{id}/coupon_rates` | POST | `coupon-rates create <id>` |
| `/coupon_rates/{id}` | PUT | `coupon-rates update <id>` |
| `/coupon_rates/{id}` | DELETE | `coupon-rates delete <id>` |

### Reference Data

| Endpoint | Method | CLI Command |
|----------|--------|-------------|
| `/countries` | GET | `countries` |

## Implementation Checklist

- [x] Project setup (pyproject.toml, directory structure)
- [x] Auth module (client credentials flow, token storage)
- [x] HTTP client (GET, POST methods)
- [x] HTTP client (PUT, DELETE methods)
- [x] API module (portfolio, holdings read endpoints)
- [x] API module (holdings update/delete)
- [x] API module (custom investments CRUD)
- [x] API module (prices CRUD)
- [x] API module (coupon rates CRUD)
- [x] CLI module (read commands)
- [x] CLI module (write commands)
- [x] SKILL.md (OpenClaw skill definition)
- [x] README.md (user documentation)
- [x] Test suite (base tests)
- [x] Test suite (CRUD tests)

## Testing

```bash
# Install with dev dependencies
cd sharesight-skill && uv sync --extra dev

# Run test suite
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
| `tests/test_client.py` | 11+ | HTTP requests, error handling, 401 retry, PUT/DELETE |
| `tests/test_cli.py` | 20+ | Argument parsing, all CLI commands |

## Notes

- Sharesight access tokens expire after 30 minutes
- API is in closed beta - contact Sharesight for access
- Base URL: `https://api.sharesight.com/api/v3/`
