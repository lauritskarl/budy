from enum import Enum
from pathlib import Path
from typing import Annotated

from rich.console import Console
from sqlmodel import Session
from typer import Exit, Option, Typer

import budy.importers as importers
from budy.database import engine
from budy.views import render_error, render_success, render_warning

app = Typer(no_args_is_help=True)
console = Console()


class Bank(str, Enum):
    LHV = "LHV"
    SEB = "SEB"
    SWEDBANK = "Swedbank"


@app.command(name="import")
# @app.command(name="i", hidden=True)
def import_transactions(
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
    if bank == Bank.LHV:
        importer = importers.LHVImporter()
    elif bank == Bank.SEB:
        importer = importers.SEBImporter()
    elif bank == Bank.SWEDBANK:
        importer = importers.SwedbankImporter()
    else:
        console.print(render_error(f"No importer found for {bank}"))
        raise Exit(1)

    console.print(
        f"Parsing [bold]{file_path.name}[/] using [cyan]{importer.__class__.__name__}[/]..."
    )

    try:
        transactions = importer.process_file(file_path)
    except Exception as e:
        console.print(render_error(str(e)))
        raise Exit(code=1)

    if not transactions:
        console.print(render_warning(f"No valid expenses found in {file_path.name}."))
        return

    total_amount = sum(t.amount for t in transactions)
    console.print(
        f"\nFound [bold]{len(transactions)}[/] transactions totaling [green]${total_amount / 100:,.2f}[/]."
    )

    if dry_run:
        console.print("[yellow]Dry run active. No changes made to database.[/]")
        return

    with Session(engine) as session:
        session.add_all(transactions)
        session.commit()

        console.print(
            render_success(f"Successfully imported {len(transactions)} transactions!")
        )


if __name__ == "__main__":
    app()
