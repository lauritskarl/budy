from datetime import date

from rich.table import Table

from budy.models import Transaction


def render_transaction_list(
    daily_transactions: list[tuple[date, list[Transaction]]],
) -> Table:
    """Renders a table of transactions."""
    page_total = sum(
        t.amount for _, transactions in daily_transactions for t in transactions
    )

    table = Table(title="Transaction History", show_footer=True)
    table.add_column("ID", justify="right", style="dim")
    table.add_column("Entry Date", justify="right", style="cyan", footer="Page Total:")
    table.add_column("Amount", justify="right", style="green", footer=f"${page_total}")

    for day, transactions in daily_transactions:
        date_str = day.strftime("%b %d, %Y")

        if not transactions:
            table.add_row("-", date_str, "[dim italic]Nothing to show[/]")
            continue

        for transaction in transactions:
            table.add_row(str(transaction.id), date_str, f"${transaction.amount}")

    return table
