from rich.panel import Panel
from rich.table import Table

from budy.models import Budget


def render_budget_status(
    budget: Budget | None,
    total_spent: int,
    month_name: str,
    target_year: int,
) -> Panel:
    """Renders the monthly budget status panel with a progress bar."""
    BAR_WIDTH = 30
    TOTAL_WIDTH = BAR_WIDTH + 1 + 4

    spent_display = total_spent / 100.0

    if not budget:
        stats_table = Table.grid(padding=(0, 2))
        stats_table.add_column(style="dim")
        stats_table.add_column(justify="right")

        stats_table.add_row("Budgeted:", "-")
        stats_table.add_row("Spent:", f"[bold]${spent_display:,.2f}[/bold]")
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

    stats_table.add_row("Budgeted:", f"${budget_display:,.2f}")
    stats_table.add_row("Spent:", f"[bold {color}]${spent_display:,.2f}[/]")
    stats_table.add_row("Remaining:", f"${remaining_display:,.2f}")

    filled_len = min(int((total_spent / budget.amount) * BAR_WIDTH), BAR_WIDTH)
    empty_len = BAR_WIDTH - filled_len
    bar_filled = "━" * filled_len
    bar_empty = "━" * empty_len
    progress_bar = f"[{color}]{bar_filled}[/][dim]{bar_empty}[/]"

    content = Table.grid()
    content.add_row(stats_table)
    content.add_row("")
    content.add_row(f"{progress_bar} [bold]{int(percent_spent):>3}%[/]")

    return Panel(
        content,
        title=f"[b]{month_name} {target_year}[/]",
        subtitle=f"[bold {color}]{status_msg}[/]",
        expand=False,
        border_style=color,
    )
