from pathlib import Path
from typing import Annotated

from rich.console import Console
from sqlmodel import Session
from typer import Exit, Option, Typer

from budy.database import engine
from budy.schemas import Bank
from budy.services.transaction import import_transactions
from budy.views import render_error, render_import_summary

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="import")
def run_import(
    bank: Annotated[
        Bank,
        Option(
            "--bank",
            "-b",
            prompt=True,
            help="The bank to import from.",
            case_sensitive=False,
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
        f"Parsing [bold]{file_path.name}[/] using [cyan]{bank.value}[/] importer..."
    )

    try:
        with Session(engine) as session:
            transactions = import_transactions(
                session=session,
                bank=bank,
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


if __name__ == "__main__":
    app()
