# Sharesight Skill - Implementation Notes

## Overview

OpenClaw skill for the Sharesight API. Uses Python with uv, OAuth 2.0 Client Credentials flow, and focuses on read-only portfolio operations.

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
    ├── test_auth.py         # 15 tests for OAuth and token management
    ├── test_client.py       # 11 tests for HTTP client and errors
    └── test_cli.py          # 20 tests for CLI commands
```

## Key Design Decisions

1. **Minimal dependencies**: Only `httpx` for HTTP. Uses stdlib `argparse` for CLI.
2. **OAuth Client Credentials**: Simpler than authorization_code, suitable for personal use.
3. **Token caching**: Stored in `~/.config/sharesight-cli/config.json` with auto-refresh.
4. **JSON output**: All commands output JSON for easy parsing by agents.

## API Coverage

### Implemented (Read-only)

| Endpoint | Method | CLI Command |
|----------|--------|-------------|
| `/portfolios` | GET | `portfolios list` |
| `/portfolios/{id}` | GET | `portfolios get <id>` |
| `/portfolios/{id}/holdings` | GET | `portfolios holdings <id>` |
| `/portfolios/{id}/performance` | GET | `portfolios performance <id>` |
| `/portfolios/{id}/performance_index_chart` | GET | `portfolios chart <id>` |
| `/holdings` | GET | `holdings list` |
| `/holdings/{id}` | GET | `holdings get <id>` |
| `/countries` | GET | `countries` |

### Not Implemented (Write operations)

- Custom investments (CRUD)
- Custom investment prices
- Coupon rates
- Holding updates

## Implementation Checklist

- [x] Project setup (pyproject.toml, directory structure)
- [x] Auth module (client credentials flow, token storage)
- [x] HTTP client (authenticated requests, token refresh)
- [x] API module (portfolio, holdings, performance endpoints)
- [x] CLI module (argparse commands)
- [x] SKILL.md (OpenClaw skill definition)
- [x] README.md (user documentation)
- [x] Test suite (46 tests with pytest)

## Testing

```bash
# Install with dev dependencies
cd sharesight-skill && uv sync --extra dev

# Run test suite (46 tests)
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
| `tests/test_client.py` | 11 | HTTP requests, error handling, 401 retry |
| `tests/test_cli.py` | 20 | Argument parsing, all CLI commands |

## Notes

- Sharesight access tokens expire after 30 minutes
- API is in closed beta - contact Sharesight for access
- Base URL: `https://api.sharesight.com/api/v3/`
