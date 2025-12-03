import calendar

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from budy.models import Budget, Transaction

console = Console()


def render_error(message: str) -> None:
    """Helper for consistent error message styling."""
    console.print(f"[red]{message}[/red]")


def render_warning(message: str) -> None:
    """Helper for consistent warning message styling."""
    console.print(f"[yellow]{message}[/yellow]")


def render_success(message: str) -> None:
    """Helper for consistent success message styling."""
    console.print(f"[green]{message}[/green]")


def render_budget_status(
    budget: Budget, total_spent: int, month_name: str, year: int
) -> None:
    """Renders the monthly budget status panel with a progress bar."""
    remaining = budget.amount - total_spent
    percent_spent = (total_spent / budget.amount) * 100 if budget.amount > 0 else 0

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

    stats_table.add_row("Budgeted:", f"${budget.amount:,.2f}")
    stats_table.add_row("Spent:", f"[bold {color}]${total_spent:,.2f}[/]")
    stats_table.add_row("Remaining:", f"${remaining:,.2f}")

    bar_width = 30
    filled_len = min(int((total_spent / budget.amount) * bar_width), bar_width)
    empty_len = bar_width - filled_len
    bar_filled = "━" * filled_len
    bar_empty = "━" * empty_len
    progress_bar = f"[{color}]{bar_filled}[/][dim]{bar_empty}[/]"

    content = Table.grid()
    content.add_row(stats_table)
    content.add_row("")
    content.add_row(f"{progress_bar} [bold]{int(percent_spent)}%[/]")

    console.print(
        Panel(
            content,
            title=f"[b]{month_name} {year}[/b]",
            subtitle=f"[bold {color}]{status_msg}[/]",
            expand=False,
            border_style=color,
        )
    )


def render_transaction_list(transactions: list[Transaction], page_total: int) -> None:
    """Renders a table of transactions."""
    table = Table(title="Transaction History", show_footer=True)
    table.add_column("ID", justify="right", style="dim")
    table.add_column("Entry Date", justify="right", style="cyan", footer="Page Total:")
    table.add_column("Amount", justify="right", style="green", footer=f"${page_total}")

    for transaction in transactions:
        date_str = transaction.entry_date.strftime("%b %d, %Y")
        table.add_row(str(transaction.id), date_str, f"${transaction.amount}")

    console.print(table)


def render_budget_list(budgets: list[Budget], year: int) -> None:
    """Renders a list of budgets for a specific year."""
    total_budgeted = sum(b.amount for b in budgets)

    table = Table(title=f"Budget List ({year})", show_footer=True)

    table.add_column("ID", justify="right", style="dim")
    table.add_column("Month", style="cyan", footer="Total Budgeted:")
    table.add_column(
        "Amount", justify="right", style="green", footer=f"${total_budgeted}"
    )

    for budget in budgets:
        month_name = calendar.month_name[budget.target_month]
        table.add_row(
            str(budget.id),
            month_name,
            f"${budget.amount}",
        )

    console.print(table)
