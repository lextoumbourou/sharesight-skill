---
name: sharesight
version: 1.0.0
description: Access Sharesight portfolio data via the API
metadata: {"openclaw": {"category": "finance", "requires": {"env": ["SHARESIGHT_CLIENT_ID", "SHARESIGHT_CLIENT_SECRET"]}}}
---

# Sharesight Skill

Access Sharesight portfolio management data including portfolios, holdings, and performance reports.

## Prerequisites

Set these environment variables:
- `SHARESIGHT_CLIENT_ID` - Your Sharesight API client ID
- `SHARESIGHT_CLIENT_SECRET` - Your Sharesight API client secret

## Commands

### Authentication

```bash
# Authenticate (required before first use)
sharesight auth login

# Check authentication status
sharesight auth status

# Clear saved token
sharesight auth clear
```

### Portfolios

```bash
# List all portfolios
sharesight portfolios list
sharesight portfolios list --consolidated

# Get portfolio details
sharesight portfolios get <portfolio_id>

# List holdings in a portfolio
sharesight portfolios holdings <portfolio_id>

# Get performance report
sharesight portfolios performance <portfolio_id>
sharesight portfolios performance <portfolio_id> --start-date 2024-01-01 --end-date 2024-12-31
sharesight portfolios performance <portfolio_id> --grouping market --include-sales

# Get performance chart data
sharesight portfolios chart <portfolio_id>
sharesight portfolios chart <portfolio_id> --benchmark SPY.NYSE
```

### Holdings

```bash
# List all holdings across portfolios
sharesight holdings list

# Get holding details
sharesight holdings get <holding_id>
sharesight holdings get <holding_id> --avg-price --cost-base
sharesight holdings get <holding_id> --values-over-time true
```

### Reference Data

```bash
# List country codes
sharesight countries
sharesight countries --supported
```

## Output Format

All commands output JSON. Example portfolio list response:

```json
{
  "portfolios": [
    {
      "id": 12345,
      "name": "My Portfolio",
      "currency_code": "AUD",
      "country_code": "AU"
    }
  ]
}
```

## Date Format

All dates use `YYYY-MM-DD` format (e.g., `2024-01-15`).

## Grouping Options

Performance reports support these grouping options:
- `country` - Group by country
- `currency` - Group by currency
- `market` - Group by market (default)
- `portfolio` - Group by portfolio
- `sector_classification` - Group by sector
- `industry_classification` - Group by industry
- `investment_type` - Group by investment type
- `ungrouped` - No grouping

## Common Workflows

### View Portfolio Performance

```bash
# Get current year performance
sharesight portfolios performance 12345 --start-date 2024-01-01

# Compare against S&P 500
sharesight portfolios chart 12345 --benchmark SPY.NYSE
```

### Analyze Holdings

```bash
# List all holdings with cost information
sharesight holdings get 67890 --avg-price --cost-base
```
