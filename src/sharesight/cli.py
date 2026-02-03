"""CLI interface for Sharesight API using argparse."""

import argparse
import json
import sys
from typing import Any

from . import __version__
from .api import SharesightAPI
from .auth import get_token, is_authenticated, clear_token
from .client import APIError


def print_json(data: Any) -> None:
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2))


def cmd_auth(args: argparse.Namespace) -> int:
    """Authenticate with Sharesight API."""
    try:
        token = get_token(force_refresh=True)
        print(json.dumps({"status": "authenticated", "message": "Successfully authenticated with Sharesight API"}))
        return 0
    except ValueError as e:
        print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        return 1


def cmd_auth_status(args: argparse.Namespace) -> int:
    """Check authentication status."""
    authenticated = is_authenticated()
    print(json.dumps({"authenticated": authenticated}))
    return 0 if authenticated else 1


def cmd_auth_clear(args: argparse.Namespace) -> int:
    """Clear saved authentication token."""
    clear_token()
    print(json.dumps({"status": "success", "message": "Token cleared"}))
    return 0


def cmd_portfolios_list(args: argparse.Namespace) -> int:
    """List all portfolios."""
    with SharesightAPI() as api:
        result = api.list_portfolios(consolidated=args.consolidated)
        print_json(result)
    return 0


def cmd_portfolios_get(args: argparse.Namespace) -> int:
    """Get a specific portfolio."""
    with SharesightAPI() as api:
        result = api.get_portfolio(args.id, consolidated=args.consolidated)
        print_json(result)
    return 0


def cmd_portfolios_holdings(args: argparse.Namespace) -> int:
    """List holdings for a portfolio."""
    with SharesightAPI() as api:
        result = api.list_portfolio_holdings(args.id, consolidated=args.consolidated)
        print_json(result)
    return 0


def cmd_portfolios_performance(args: argparse.Namespace) -> int:
    """Get performance report for a portfolio."""
    with SharesightAPI() as api:
        result = api.get_portfolio_performance(
            args.id,
            start_date=args.start_date,
            end_date=args.end_date,
            consolidated=args.consolidated,
            include_sales=args.include_sales,
            grouping=args.grouping,
        )
        print_json(result)
    return 0


def cmd_portfolios_chart(args: argparse.Namespace) -> int:
    """Get performance index chart data."""
    with SharesightAPI() as api:
        result = api.get_portfolio_performance_chart(
            args.id,
            start_date=args.start_date,
            end_date=args.end_date,
            consolidated=args.consolidated,
            grouping=args.grouping,
            benchmark_code=args.benchmark,
        )
        print_json(result)
    return 0


def cmd_holdings_list(args: argparse.Namespace) -> int:
    """List all holdings."""
    with SharesightAPI() as api:
        result = api.list_holdings()
        print_json(result)
    return 0


def cmd_holdings_get(args: argparse.Namespace) -> int:
    """Get a specific holding."""
    with SharesightAPI() as api:
        result = api.get_holding(
            args.id,
            average_purchase_price=args.avg_price,
            cost_base=args.cost_base,
            values_over_time=args.values_over_time,
        )
        print_json(result)
    return 0


def cmd_countries(args: argparse.Namespace) -> int:
    """List country definitions."""
    with SharesightAPI() as api:
        supported = None
        if args.supported:
            supported = True
        elif args.unsupported:
            supported = False
        result = api.list_countries(supported=supported)
        print_json(result)
    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="sharesight",
        description="CLI for accessing Sharesight portfolio data via the API",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Auth commands
    auth_parser = subparsers.add_parser("auth", help="Authentication commands")
    auth_subparsers = auth_parser.add_subparsers(dest="auth_command")

    auth_subparsers.add_parser("login", help="Authenticate with Sharesight API")
    auth_subparsers.add_parser("status", help="Check authentication status")
    auth_subparsers.add_parser("clear", help="Clear saved authentication token")

    # Portfolios commands
    portfolios_parser = subparsers.add_parser("portfolios", help="Portfolio commands")
    portfolios_subparsers = portfolios_parser.add_subparsers(dest="portfolios_command")

    # portfolios list
    p_list = portfolios_subparsers.add_parser("list", help="List all portfolios")
    p_list.add_argument("--consolidated", action="store_true", help="Show consolidated portfolio views")

    # portfolios get
    p_get = portfolios_subparsers.add_parser("get", help="Get a specific portfolio")
    p_get.add_argument("id", type=int, help="Portfolio ID")
    p_get.add_argument("--consolidated", action="store_true", help="Portfolio is consolidated")

    # portfolios holdings
    p_holdings = portfolios_subparsers.add_parser("holdings", help="List holdings for a portfolio")
    p_holdings.add_argument("id", type=int, help="Portfolio ID")
    p_holdings.add_argument("--consolidated", action="store_true", help="Consolidated view")

    # portfolios performance
    p_perf = portfolios_subparsers.add_parser("performance", help="Get performance report")
    p_perf.add_argument("id", type=int, help="Portfolio ID")
    p_perf.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    p_perf.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    p_perf.add_argument("--consolidated", action="store_true", help="Consolidated view")
    p_perf.add_argument("--include-sales", action="store_true", help="Include sales")
    p_perf.add_argument(
        "--grouping",
        choices=["country", "currency", "market", "portfolio", "sector_classification", "industry_classification", "investment_type", "ungrouped"],
        help="Group holdings by attribute",
    )

    # portfolios chart
    p_chart = portfolios_subparsers.add_parser("chart", help="Get performance index chart data")
    p_chart.add_argument("id", type=int, help="Portfolio ID")
    p_chart.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    p_chart.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    p_chart.add_argument("--consolidated", action="store_true", help="Consolidated view")
    p_chart.add_argument("--grouping", help="Group by attribute")
    p_chart.add_argument("--benchmark", help="Benchmark code (e.g., SPY.NYSE)")

    # Holdings commands
    holdings_parser = subparsers.add_parser("holdings", help="Holdings commands")
    holdings_subparsers = holdings_parser.add_subparsers(dest="holdings_command")

    # holdings list
    holdings_subparsers.add_parser("list", help="List all holdings")

    # holdings get
    h_get = holdings_subparsers.add_parser("get", help="Get a specific holding")
    h_get.add_argument("id", type=int, help="Holding ID")
    h_get.add_argument("--avg-price", action="store_true", help="Include average purchase price")
    h_get.add_argument("--cost-base", action="store_true", help="Include cost base")
    h_get.add_argument("--values-over-time", help="'true' or start date for values over time")

    # Countries command
    countries_parser = subparsers.add_parser("countries", help="List country definitions")
    countries_parser.add_argument("--supported", action="store_true", help="Only show supported countries")
    countries_parser.add_argument("--unsupported", action="store_true", help="Only show unsupported countries")

    return parser


def main() -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        # Auth commands
        if args.command == "auth":
            if args.auth_command == "login" or args.auth_command is None:
                return cmd_auth(args)
            elif args.auth_command == "status":
                return cmd_auth_status(args)
            elif args.auth_command == "clear":
                return cmd_auth_clear(args)

        # Portfolios commands
        elif args.command == "portfolios":
            if args.portfolios_command == "list" or args.portfolios_command is None:
                return cmd_portfolios_list(args)
            elif args.portfolios_command == "get":
                return cmd_portfolios_get(args)
            elif args.portfolios_command == "holdings":
                return cmd_portfolios_holdings(args)
            elif args.portfolios_command == "performance":
                return cmd_portfolios_performance(args)
            elif args.portfolios_command == "chart":
                return cmd_portfolios_chart(args)

        # Holdings commands
        elif args.command == "holdings":
            if args.holdings_command == "list" or args.holdings_command is None:
                return cmd_holdings_list(args)
            elif args.holdings_command == "get":
                return cmd_holdings_get(args)

        # Countries command
        elif args.command == "countries":
            return cmd_countries(args)

        parser.print_help()
        return 0

    except APIError as e:
        print(json.dumps({"error": e.message, "status_code": e.status_code}), file=sys.stderr)
        return 1
    except ValueError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 1
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
