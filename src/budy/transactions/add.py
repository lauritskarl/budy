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
        int,
        Option(
            "--amount",
            "-a",
            min=1,
            max=9999999,
            prompt=True,
            help="Set the transaction amount.",
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

        transaction = Transaction(amount=amount, entry_date=final_date)

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        print(
            f"[green]✓ Added![/green] Transaction [bold]#{transaction.id}[/bold]: "
            f"[bold]${transaction.amount}[/bold] on {transaction.entry_date.strftime('%B %d, %Y')}"
        )


if __name__ == "__main__":
    app()
