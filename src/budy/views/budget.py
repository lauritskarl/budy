import calendar
from typing import Optional

from rich.panel import Panel
from rich.table import Table

from budy.schemas import Budget, BudgetSuggestion, MonthlyReportData


def render_budget_list(
    *, budgets: list[tuple[int, Optional[Budget]]], target_year: int
) -> Table:
    """Renders a list of budgets for a specific year."""
    existing_budgets = [b for _, b in budgets if b]
    total_budgeted = sum(b.amount for b in existing_budgets) / 100.0

    table = Table(title=f"Budget List ({target_year})", show_footer=True)

    table.add_column("ID", justify="right", style="dim")
    table.add_column("Month", style="cyan", footer="Total Budgeted:")
    table.add_column(
        "Amount", justify="right", style="green", footer=f"${total_budgeted:,.0f}"
    )

    for month_idx, budget in budgets:
        month_name = calendar.month_name[month_idx]

        if budget:
            table.add_row(
                str(budget.id),
                month_name,
                f"${budget.amount / 100.0:,.0f}",
            )
        else:
            table.add_row(
                "-",
                f"[dim]{month_name}[/]",
                "[dim italic]Not set[/]",
            )

    return table


def render_budget_preview(*, suggestions: list[BudgetSuggestion], year: int) -> Table:
    """Renders the comparison table of current vs suggested budgets."""
    table = Table(title=f"Suggested Budgets ({year})")
    table.add_column("Month", style="cyan")
    table.add_column("Current", justify="right", style="dim")
    table.add_column("Suggested", justify="right", style="green")

    for item in suggestions:
        current_str = "-"
        if item.existing:
            current_str = f"${item.existing.amount / 100:,.0f}"

        suggested_str = f"${item.amount / 100:,.0f}"

        table.add_row(item.month_name, current_str, suggested_str)

    return table


def render_budget_status(*, data: MonthlyReportData) -> Panel:
    """Renders the monthly budget status panel with a progress bar and optional forecast."""
    BAR_WIDTH = 30
    TOTAL_WIDTH = BAR_WIDTH + 1 + 4

    budget = data.budget
    total_spent = data.total_spent
    month_name = data.month_name
    target_year = data.target_year

    spent_display = total_spent / 100.0

    if not budget:
        stats_table = Table.grid(padding=(0, 2))
        stats_table.add_column(style="dim")
        stats_table.add_column(justify="right")

        stats_table.add_row("Budgeted:", "-")
        stats_table.add_row("Spent:", f"[bold]${spent_display:,.0f}[/bold]")
        stats_table.add_row("Remaining:", "-")

        content = Table.grid()
        content.add_row(stats_table)
        content.add_row("")

        dummy_bar = " " * TOTAL_WIDTH
        content.add_row(dummy_bar)

        return Panel(
            content,
            title=f"[dim]{month_name} {target_year}[/]",
            subtitle="[dim]NO LIMIT[/]",
            border_style="dim",
            expand=False,
        )

    remaining = budget.amount - total_spent
    percent_spent = (total_spent / budget.amount) * 100 if budget.amount > 0 else 0

    budget_display = budget.amount / 100.0
    remaining_display = remaining / 100.0

    if total_spent > budget.amount:
        color = "red"
        status_msg = "OVER BUDGET"
    elif total_spent >= budget.amount * 0.9:
        color = "yellow"
        status_msg = "NEAR LIMIT"
    else:
        color = "green"
        status_msg = "ON TRACK"

    stats_table = Table.grid(padding=(0, 2))
    stats_table.add_column(style="cyan")
    stats_table.add_column(justify="right")

    stats_table.add_row("Budgeted:", f"${budget_display:,.0f}")
    stats_table.add_row("Spent:", f"[bold {color}]${spent_display:,.0f}[/]")
    stats_table.add_row("Remaining:", f"${remaining_display:,.0f}")

    filled_len = min(int((total_spent / budget.amount) * BAR_WIDTH), BAR_WIDTH)
    empty_len = BAR_WIDTH - filled_len
    bar_filled = "━" * filled_len
    bar_empty = "━" * empty_len
    progress_bar = f"[{color}]{bar_filled}[/][dim]{bar_empty}[/]"

    content = Table.grid()
    content.add_row(stats_table)
    content.add_row("")
    content.add_row(f"{progress_bar} [bold]{int(percent_spent):>3}%[/]")

    if data.forecast:
        grid = Table.grid(padding=(0, 2))
        grid.add_column(style="dim italic")
        grid.add_column(justify="right")

        avg_per_day = data.forecast.avg_per_day
        projected_total = data.forecast.projected_total
        projected_overage = data.forecast.projected_overage

        grid.add_row("Daily Average:", f"${avg_per_day / 100:,.0f}")
        grid.add_row("Projected Total:", f"[bold]${projected_total / 100:,.0f}[/]")

        if projected_overage is not None and projected_overage > 0:
            grid.add_row(
                "Projected Overage:", f"[red]+${projected_overage / 100:,.0f}[/]"
            )

        content.add_row("\n[bold underline]Forecast[/]")
        content.add_row(grid)

    return Panel(
        content,
        title=f"[b]{month_name} {target_year}[/]",
        subtitle=f"[bold {color}]{status_msg}[/]",
        expand=False,
        border_style=color,
    )
