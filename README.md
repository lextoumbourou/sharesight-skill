# Sharesight CLI

A command-line interface for accessing Sharesight portfolio data via the API.

## Installation

```bash
# Install with uv
uv pip install -e .

# Or install from source
uv sync
```

## Configuration

Set your Sharesight API credentials as environment variables:

```bash
export SHARESIGHT_CLIENT_ID="your_client_id"
export SHARESIGHT_CLIENT_SECRET="your_client_secret"
```

To obtain API credentials:
1. Email Sharesight to request API access (following instructions in [Getting Started](https://portfolio.sharesight.com/api/)).
2. Once enabled, find your credentials under **Account** > **Sharesight API**

## Usage

### Authenticate

```bash
sharesight auth login
```

### List Portfolios

```bash
sharesight portfolios list
```

### Get Portfolio Performance

```bash
sharesight portfolios performance 12345 --start-date 2024-01-01 --end-date 2024-12-31
```

### List Holdings

```bash
sharesight holdings list
```

### Get Help

```bash
sharesight --help
sharesight portfolios --help
```

## Output

All commands output JSON to stdout. Errors are written to stderr.

## Token Storage

Access tokens are cached in `~/.config/sharesight-cli/config.json` and automatically refreshed when expired (tokens are valid for 30 minutes).

## Development

```bash
# Install development dependencies
uv sync

# Run directly
uv run sharesight portfolios list

# Run tests
uv run pytest
```

## License

MIT
