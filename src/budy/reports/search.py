from typing import Annotated

from rich.console import Console
from rich.table import Table
from sqlmodel import Session, col, desc, or_, select
from typer import Argument, Option, Typer

from budy.database import engine
from budy.models import Transaction
from budy.views import render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="search")
@app.command(name="s", hidden=True)
def search_transactions(
    query: Annotated[
        str,
        Argument(help="Keyword to search for (in receiver or description)."),
    ],
    limit: Annotated[
        int,
        Option(
            "--limit",
            "-l",
            min=1,
            help="Maximum number of results to display.",
        ),
    ] = 20,
) -> None:
    """
    Search transactions by keyword.
    Looks inside the Receiver name and Description.
    """
    with Session(engine) as session:
        pattern = f"%{query}%"

        stmt = (
            select(Transaction)
            .where(
                or_(
                    col(Transaction.receiver).ilike(pattern),
                    col(Transaction.description).ilike(pattern),
                )
            )
            .order_by(desc(Transaction.entry_date))
            .limit(limit)
        )

        results = session.exec(stmt).all()

        if not results:
            console.print(render_warning(f"No transactions found matching '{query}'."))
            return

        title = f"Search Results: '{query}'"
        if len(results) == limit:
            title += f" (Showing latest {limit})"

        display_results = list(results)
        display_results.reverse()

        total_cents = sum(t.amount for t in display_results)

        table = Table(title=title, show_footer=True)
        table.add_column("Date", style="cyan")
        table.add_column("Receiver", style="white")
        table.add_column("Description", style="dim", footer="Total:")
        table.add_column(
            "Amount",
            justify="right",
            style="red bold",
            footer=f"${total_cents / 100:,.2f}",
        )

        for t in display_results:
            receiver = t.receiver if t.receiver else "[dim]-[/]"
            desc_text = t.description if t.description else ""

            if len(desc_text) > 30:
                desc_text = desc_text[:27] + "..."

            table.add_row(
                t.entry_date.strftime("%b %d, %Y"),
                receiver,
                desc_text,
                f"${t.amount / 100:,.2f}",
            )

        console.print(table)
