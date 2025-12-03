from datetime import date, datetime
from typing import Annotated, Optional

from rich.console import Console
from typer import Option, Typer

from budy.services.transaction import create_transaction

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="add")
def add_transaction(
    amount: Annotated[
        float,
        Option(
            "--amount",
            "-a",
            min=0.01,
            max=9999999,
            prompt=True,
            help="Set the transaction amount (in dollars/euros).",
        ),
    ],
    entry_date: Annotated[
        Optional[datetime],
        Option(
            "--date",
            "-d",
            formats=["%Y-%m-%d", "%Y/%m/%d"],
            help="Set the transaction date (YYYY-MM-DD).",
        ),
    ] = None,
) -> None:
    """Add a new transaction to the database."""
    final_date = entry_date.date() if entry_date else date.today()
    transaction = create_transaction(amount=amount, entry_date=final_date)

    console.print(
        f"[green]✓ Added![/] Transaction [bold]#{transaction.id}[/]: "
        f"[bold]${transaction.amount / 100:,.2f}[/bold] on {transaction.entry_date.strftime('%B %d, %Y')}"
    )


if __name__ == "__main__":
    app()
