"""Sharesight API endpoint methods."""

from typing import Any, Optional

from .client import SharesightClient


class SharesightAPI:
    """High-level API for Sharesight operations."""

    def __init__(self, client: Optional[SharesightClient] = None):
        self._client = client or SharesightClient()
        self._owns_client = client is None

    def close(self) -> None:
        """Close the API client if we own it."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "SharesightAPI":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    # -------------------------------------------------------------------------
    # Portfolios
    # -------------------------------------------------------------------------

    def list_portfolios(self, consolidated: bool = False) -> dict[str, Any]:
        """List all portfolios for the authenticated user.

        Args:
            consolidated: Set to True to see consolidated portfolio views.

        Returns:
            API response with portfolios list.
        """
        params = {}
        if consolidated:
            params["consolidated"] = "true"
        return self._client.get("/portfolios", params=params if params else None)

    def get_portfolio(self, portfolio_id: int, consolidated: bool = False) -> dict[str, Any]:
        """Get a specific portfolio by ID.

        Args:
            portfolio_id: The portfolio ID.
            consolidated: Set to True if the portfolio is consolidated.

        Returns:
            API response with portfolio details.
        """
        params = {}
        if consolidated:
            params["consolidated"] = "true"
        return self._client.get(f"/portfolios/{portfolio_id}", params=params if params else None)

    def list_portfolio_holdings(self, portfolio_id: int, consolidated: bool = False) -> dict[str, Any]:
        """List holdings for a specific portfolio.

        Args:
            portfolio_id: The portfolio ID.
            consolidated: True if a consolidated view is requested.

        Returns:
            API response with holdings list.
        """
        params = {}
        if consolidated:
            params["consolidated"] = "true"
        return self._client.get(f"/portfolios/{portfolio_id}/holdings", params=params if params else None)

    def get_portfolio_performance(
        self,
        portfolio_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        consolidated: bool = False,
        include_sales: bool = False,
        grouping: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get performance report for a portfolio.

        Args:
            portfolio_id: The portfolio ID.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            consolidated: Set to True for consolidated portfolio views.
            include_sales: Pass True to include sales.
            grouping: Group by attribute (country, currency, market, etc.).

        Returns:
            API response with performance report.
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if consolidated:
            params["consolidated"] = "true"
        if include_sales:
            params["include_sales"] = "true"
        if grouping:
            params["grouping"] = grouping
        return self._client.get(f"/portfolios/{portfolio_id}/performance", params=params if params else None)

    def get_portfolio_performance_chart(
        self,
        portfolio_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        consolidated: bool = False,
        grouping: Optional[str] = None,
        benchmark_code: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get performance index chart data for a portfolio.

        Args:
            portfolio_id: The portfolio ID.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            consolidated: True if a consolidated view is requested.
            grouping: Group by attribute (country, currency, market, etc.).
            benchmark_code: Benchmark code and market (e.g., SPY.NYSE).

        Returns:
            API response with chart data.
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if consolidated:
            params["consolidated"] = "true"
        if grouping:
            params["grouping"] = grouping
        if benchmark_code:
            params["benchmark_code"] = benchmark_code
        return self._client.get(
            f"/portfolios/{portfolio_id}/performance_index_chart", params=params if params else None
        )

    # -------------------------------------------------------------------------
    # Holdings
    # -------------------------------------------------------------------------

    def list_holdings(self) -> dict[str, Any]:
        """List all holdings across all portfolios.

        Returns:
            API response with holdings list.
        """
        return self._client.get("/holdings")

    def get_holding(
        self,
        holding_id: int,
        average_purchase_price: bool = False,
        cost_base: bool = False,
        values_over_time: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get a specific holding by ID.

        Args:
            holding_id: The holding ID.
            average_purchase_price: Include average purchase price.
            cost_base: Include cost base.
            values_over_time: 'true' for values from inception, or a date string.

        Returns:
            API response with holding details.
        """
        params = {}
        if average_purchase_price:
            params["average_purchase_price"] = "true"
        if cost_base:
            params["cost_base"] = "true"
        if values_over_time:
            params["values_over_time"] = values_over_time
        return self._client.get(f"/holdings/{holding_id}", params=params if params else None)

    # -------------------------------------------------------------------------
    # Reference Data
    # -------------------------------------------------------------------------

    def list_countries(self, supported: Optional[bool] = None) -> dict[str, Any]:
        """Get list of country definitions.

        Args:
            supported: Filter by supported status if specified.

        Returns:
            API response with countries list.
        """
        params = {}
        if supported is not None:
            params["supported"] = "true" if supported else "false"
        return self._client.get("/countries", params=params if params else None)
