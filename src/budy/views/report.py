from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from budy.dtos import (
    MonthlyReportData,
    PayeeRankingItem,
    VolatilityReportData,
    WeekdayReportItem,
)
from budy.models import Transaction
from budy.views.budget import render_budget_status
from budy.views.transaction import render_simple_transaction_list


def render_yearly_report(
    *, monthly_reports: list[MonthlyReportData], year: int
) -> Table:
    """Renders a grid of budget status panels for the year."""
    grid = Table.grid(padding=1)
    grid.add_column()
    grid.add_column()
    grid.add_column()

    panels = [render_budget_status(data=report) for report in monthly_reports]

    for i in range(0, len(panels), 3):
        row = panels[i : i + 3]
        row += [""] * (3 - len(row))
        grid.add_row(*row)

    return grid


def render_weekday_report(*, report_data: list[WeekdayReportItem]) -> Table:
    """Renders the weekday spending analysis table."""
    total_spent = sum(d.total_amount for d in report_data)
    total_count = sum(d.count for d in report_data)

    table = Table(title="Spending Habits by Day of Week", show_footer=True)
    table.add_column("Day", style="cyan", footer="TOTAL")
    table.add_column("Avg Transaction", justify="right", style="green")
    table.add_column("Count", justify="right", style="dim", footer=str(total_count))
    table.add_column(
        "Total Spent",
        justify="right",
        style="bold",
        footer=f"${total_spent / 100:,.2f}",
    )

    for item in report_data:
        if item.count == 0:
            table.add_row(item.day_name, "-", "0", "-")
        else:
            table.add_row(
                item.day_name,
                f"${item.avg_amount / 100:,.2f}",
                str(item.count),
                f"${item.total_amount / 100:,.2f}",
            )
    return table


def render_payee_ranking(
    *,
    payees: list[PayeeRankingItem],
    title: str = "Top Payees",
) -> Table:
    """Renders a ranking table of payees."""
    table = Table(title=title, show_footer=False)
    table.add_column("Rank", style="dim", justify="right")
    table.add_column("Payee", style="cyan bold")
    table.add_column("Count", justify="right", style="white")
    table.add_column("Total", justify="right", style="green")
    table.add_column("Avg", justify="right", style="dim")

    for i, item in enumerate(payees, 1):
        table.add_row(
            f"#{i}",
            item.name,
            str(item.count),
            f"${item.total / 100:,.2f}",
            f"${item.avg / 100:,.2f}",
        )

    return table


def render_search_results(
    *,
    results: list[Transaction],
    query: str,
    limit: int,
) -> Table:
    """Renders search results in a table."""
    display_results = results[::-1]
    total_cents = sum(t.amount for t in display_results)

    title = f"Search Results: '{query}'"
    if len(results) == limit:
        title += f" (Showing latest {limit})"

    table = Table(title=title, show_footer=True)
    table.add_column("Date", style="cyan")
    table.add_column("Receiver", style="white")
    table.add_column("Description", style="dim", footer="Total:")
    table.add_column(
        "Amount",
        justify="right",
        style="red bold",
        footer=f"${total_cents / 100:,.2f}",
    )

    for t in display_results:
        desc = t.description or ""
        if len(desc) > 30:
            desc = f"{desc[:27]}..."

        table.add_row(
            t.entry_date.strftime("%b %d, %Y"),
            t.receiver or "[dim]-[/]",
            desc,
            f"${t.amount / 100:,.2f}",
        )

    return table


def render_volatility_report(*, data: VolatilityReportData, year: int | None) -> Group:
    """Renders the volatility analysis panel and outliers list."""
    cv = (data.stdev_amount / data.avg_amount) if data.avg_amount else 0

    if cv > 1.5:
        volatility_msg = "[red]High Volatility[/]"
    elif cv < 0.5:
        volatility_msg = "[green]Low Volatility[/]"
    else:
        volatility_msg = "[yellow]Moderate Volatility[/]"

    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="dim")
    grid.add_column(justify="right", style="bold")
    grid.add_row("Total Transactions:", str(data.total_count))
    grid.add_row("Average Amount:", f"${data.avg_amount / 100:,.2f}")
    grid.add_row("Standard Deviation:", f"${data.stdev_amount / 100:,.2f}")

    panel = Panel(
        grid,
        title=f"Volatility Analysis {'(' + str(year) + ')' if year else '(All Time)'}",
        subtitle=volatility_msg,
        expand=False,
    )

    outliers_table = render_simple_transaction_list(
        transactions=data.outliers, title="Top 5 Highest Transactions"
    )

    return Group(panel, "", outliers_table)
