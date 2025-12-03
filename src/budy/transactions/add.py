from datetime import date, datetime
from typing import Annotated, Optional

from rich import print
from sqlmodel import Session
from typer import Option, Typer

from budy.database import engine
from budy.models import Transaction

app = Typer(no_args_is_help=True)


@app.command(name="add")
@app.command(name="a", hidden=True)
def create_transaction(
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
    with Session(engine) as session:
        final_date = entry_date.date() if entry_date else date.today()

        amount_cents = int(round(amount * 100))

        transaction = Transaction(amount=amount_cents, entry_date=final_date)

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        print(
            f"[green]✓ Added![/] Transaction [bold]#{transaction.id}[/]: "
            f"[bold]${transaction.amount:,.2f}[/bold] on {transaction.entry_date.strftime('%B %d, %Y')}"
        )


if __name__ == "__main__":
    app()
