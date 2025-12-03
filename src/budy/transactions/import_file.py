from pathlib import Path
from typing import Annotated

from rich.console import Console
from sqlmodel import Session
from typer import Exit, Option, Typer

from budy.database import engine
from budy.importers import get_bank_importers
from budy.views import render_error, render_success, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="import")
@app.command(name="i", hidden=True)
def import_transactions(
    bank: Annotated[
        str,
        Option(
            "--bank",
            "-b",
            prompt="Bank name",
            help=f"The bank to import from. Options: {', '.join(get_bank_importers().keys())}",
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
            prompt="Path to CSV file",
            help="Path to the CSV file.",
        ),
    ],
    dry_run: Annotated[
        bool,
        Option(
            "--dry-run",
            help="Parse the file but do not save to the database.",
        ),
    ] = False,
) -> None:
    """Import transactions from a bank CSV file."""
    importers = get_bank_importers()
    bank_key = bank.lower().strip()

    if bank_key not in importers:
        console.print(render_error(f"Unknown bank: '{bank}'"))
        console.print(f"Available banks: [bold]{', '.join(importers.keys())}[/]")
        raise Exit(code=1)

    importer_cls = importers[bank_key]
    importer = importer_cls()

    console.print(
        f"Parsing [bold]{file_path.name}[/] using [cyan]{importer_cls.__name__}[/]..."
    )

    transactions, result = importer.process_file(file_path)

    if not result.success:
        console.print(render_error(result.message))
        if result.error:
            console.print(f"[dim]{result.error}[/]")
        raise Exit(code=1)

    if not transactions:
        console.print(render_warning(result.message))
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
