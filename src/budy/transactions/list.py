from typing import Annotated, Optional

from rich.console import Console
from rich.table import Table
from sqlmodel import Session, desc, select
from typer import Option, Typer

from budy.database import engine
from budy.models import Transaction

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="list")
def list_transactions(
    offset: Annotated[
        Optional[int],
        Option(
            "--offset",
            "-o",
            help="Skip the first N entries.",
        ),
    ] = 0,
    limit: Annotated[
        Optional[int],
        Option(
            "--limit",
            "-l",
            help="Limit the number of entries shown.",
        ),
    ] = 7,
) -> None:
    """Display transaction history in a table."""
    with Session(engine) as session:
        transactions = session.exec(
            select(Transaction)
            .order_by(desc(Transaction.entry_date))
            .offset(offset)
            .limit(limit)
        ).all()

        if not transactions:
            console.print("[yellow]No transactions found.[/yellow]")
            return

        page_total = sum(t.amount for t in transactions)

        table = Table(title="Transaction History", show_footer=True)

        table.add_column("ID", justify="right", style="dim")

        table.add_column(
            "Entry Date",
            justify="right",
            style="cyan",
            footer="Page Total:",
        )
        table.add_column(
            "Amount",
            justify="right",
            style="green",
            footer=f"${page_total}",
        )

        for transaction in transactions:
            date_str = transaction.entry_date.strftime("%b %d, %Y")

            table.add_row(
                str(transaction.id),
                date_str,
                f"${transaction.amount}",
            )

        console.print(table)


if __name__ == "__main__":
    app()
