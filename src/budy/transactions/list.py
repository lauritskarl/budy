from collections import defaultdict
from datetime import date, timedelta
from typing import Annotated

from rich.console import Console
from sqlmodel import Session, asc, select
from typer import Option, Typer

from budy.database import engine
from budy.models import Transaction
from budy.views import render_transaction_list, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="list")
@app.command(name="ls", hidden=True)
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
    today = date.today()
    start_date = today - timedelta(days=offset)
    dates_desc = [start_date - timedelta(days=i) for i in range(limit)]
    dates_to_show = sorted(dates_desc)

    if not dates_to_show:
        console.print(render_warning("No dates selected."))
        return

    min_date = dates_to_show[0]
    max_date = dates_to_show[-1]

    with Session(engine) as session:
        transactions = list(
            session.exec(
                select(Transaction)
                .where(Transaction.entry_date >= min_date)
                .where(Transaction.entry_date <= max_date)
                .order_by(asc(Transaction.entry_date))
            ).all()
        )

        tx_map = defaultdict(list)
        for t in transactions:
            tx_map[t.entry_date].append(t)

        display_data = []
        for d in dates_to_show:
            display_data.append((d, tx_map.get(d, [])))

        console.print(render_transaction_list(display_data))


if __name__ == "__main__":
    app()
