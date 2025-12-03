import calendar
from typing import Optional

from rich.table import Table

from budy.models import Budget


def render_budget_list(
    budgets: list[tuple[int, Optional[Budget]]], target_year: int
) -> Table:
    """Renders a list of budgets for a specific year."""
    existing_budgets = [b for _, b in budgets if b]
    total_budgeted = sum(b.amount for b in existing_budgets) / 100.0

    table = Table(title=f"Budget List ({target_year})", show_footer=True)

    table.add_column("ID", justify="right", style="dim")
    table.add_column("Month", style="cyan", footer="Total Budgeted:")
    table.add_column(
        "Amount", justify="right", style="green", footer=f"${total_budgeted:,.2f}"
    )

    for month_idx, budget in budgets:
        month_name = calendar.month_name[month_idx]

        if budget:
            table.add_row(
                str(budget.id),
                month_name,
                f"${budget.amount / 100.0:,.2f}",
            )
        else:
            table.add_row(
                "-",
                f"[dim]{month_name}[/]",
                "[dim italic]Not set[/]",
            )

    return table
