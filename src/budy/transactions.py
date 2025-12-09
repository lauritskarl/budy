from datetime import date, datetime
from pathlib import Path
from typing import Annotated, Optional

from rich.console import Console
from sqlmodel import Session
from typer import Exit, Option, Typer

from budy.config import settings
from budy.database import engine
from budy.services.transaction import (
    create_transaction,
    get_transactions,
    import_transactions,
)
from budy.views.messages import (
    render_error,
    render_success,
    render_warning,
)
from budy.views.transaction import (
    render_import_summary,
    render_transaction_list,
)

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
    txn_date: Annotated[
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
    final_date = txn_date.date() if txn_date else date.today()

    with Session(engine) as session:
        transaction = create_transaction(
            session=session,
            amount=amount,
            entry_date=final_date,
        )

    console.print(
        render_success(message=f"Added! Transaction [bold]#{transaction.id}[/]")
    )

    console.print(
        f"[bold]{settings.currency_symbol}{transaction.amount / 100:,.2f}[/bold] on {transaction.entry_date.strftime('%B %d, %Y')}"
    )


@app.command(name="list")
def read_transactions(
    offset: Annotated[
        int,
        Option(
            "--offset",
            "-o",
            help="Skip the first N entries.",
        ),
    ] = 0,
    limit: Annotated[
        int,
        Option(
            "--limit",
            "-l",
            help="Limit the number of entries shown.",
        ),
    ] = 7,
) -> None:
    """Display transaction history in a table."""
    with Session(engine) as session:
        transactions = get_transactions(session=session, offset=offset, limit=limit)

    if not transactions:
        console.print(
            render_warning(message="No transactions found for the selected dates.")
        )
        return

    console.print(render_transaction_list(daily_transactions=transactions))


def get_bank_names(incomplete: str):
    """Autocomplete for available bank names."""
    for name in settings.banks.keys():
        if name.startswith(incomplete.lower()):
            yield name


@app.command(name="import")
def run_import(
    bank: Annotated[
        str,
        Option(
            "--bank",
            "-b",
            prompt=True,
            help="The bank to import from (defined in config).",
            autocompletion=get_bank_names,
        ),
    ],
    file_path: Annotated[
        Path,
        Option(
            "--file",
            "-f",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            prompt=True,
            help="Path to the CSV file.",
        ),
    ],
    dry_run: Annotated[
        bool,
        Option(
            help="Parse the file but do not save to the database.",
        ),
    ] = False,
) -> None:
    """Import transactions from a bank CSV file."""
    console.print(
        f"Parsing [bold]{file_path.name}[/] using [cyan]{bank}[/] importer..."
    )

    try:
        with Session(engine) as session:
            transactions = import_transactions(
                session=session,
                bank_name=bank,
                file_path=file_path,
                dry_run=dry_run,
            )
            console.print(
                render_import_summary(
                    transactions=transactions, filename=file_path.name, dry_run=dry_run
                )
            )
    except ValueError as e:
        console.print(render_error(message=str(e)))
        raise Exit(1)
    except Exception as e:
        console.print(render_error(message=f"Unexpected error: {e}"))
        raise Exit(1)


@app.callback()
def callback():
    """Manage transaction history."""
    ...


if __name__ == "__main__":
    app()
