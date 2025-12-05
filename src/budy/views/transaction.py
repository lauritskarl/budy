from datetime import date

from rich.console import Group
from rich.table import Table

from budy.models import Transaction
from budy.views.messages import render_success, render_warning


def render_transaction_list(
    daily_transactions: list[tuple[date, list[Transaction]]],
) -> Table:
    """Renders a table of transactions grouped by date."""
    page_total_cents = sum(
        t.amount for _, transactions in daily_transactions for t in transactions
    )

    table = Table(title="Transaction History", show_footer=True)
    table.add_column("ID", justify="right", style="dim")
    table.add_column("Date", justify="right", style="cyan", footer="Page Total:")

    table.add_column("Receiver / Description", style="white")

    table.add_column(
        "Amount",
        justify="right",
        style="green",
        footer=f"${page_total_cents / 100:,.2f}",
    )

    for day, transactions in daily_transactions:
        date_str = day.strftime("%b %d")

        if not transactions:
            table.add_row("-", date_str, "-", "[dim italic]Nothing to show[/]")
            continue

        for t in transactions:
            details_parts = []
            if t.receiver:
                details_parts.append(f"[bold]{t.receiver}[/]")
            if t.description:
                desc = t.description
                if len(desc) > 60:
                    desc = desc[:57] + "..."
                details_parts.append(f"[dim]{desc}[/]")

            details_str = "\n".join(details_parts) if details_parts else "[dim]-[/]"

            table.add_row(str(t.id), date_str, details_str, f"${t.amount / 100:,.2f}")

    return table


def render_simple_transaction_list(
    transactions: list[Transaction], title: str = "Transactions"
) -> Table:
    """Renders a simple flat list of transactions (e.g. for outliers)."""
    table = Table(title=title, show_footer=False)
    table.add_column("Date", style="cyan")
    table.add_column("Receiver", style="white")
    table.add_column("Description", style="dim")
    table.add_column("Amount", justify="right", style="red bold")

    for t in transactions:
        receiver = t.receiver if t.receiver else "[dim]-[/]"
        desc = t.description if t.description else ""

        if len(desc) > 30:
            desc = desc[:27] + "..."

        table.add_row(
            t.entry_date.strftime("%b %d, %Y"),
            receiver,
            desc,
            f"${t.amount / 100:,.2f}",
        )

    return table


def render_import_summary(
    transactions: list[Transaction], filename: str, dry_run: bool
) -> Group | str:
    """Renders the post-import summary message."""
    if not transactions:
        return render_warning(f"No valid expenses found in {filename}.")

    count = len(transactions)
    total_display = sum(t.amount for t in transactions) / 100.0

    summary_text = f"\nFound [bold]{count}[/] transactions totaling [green]${total_display:,.2f}[/]."

    if dry_run:
        status_text = "[yellow]Dry run active. No changes made to database.[/]"
    else:
        status_text = render_success(f"Successfully imported {count} transactions!")

    return Group(summary_text, status_text)
