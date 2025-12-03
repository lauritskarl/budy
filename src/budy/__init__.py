from sqlmodel import SQLModel
from typer import Typer

from budy.budgets import app as budgets_app
from budy.database import engine
from budy.report import app as report_app
from budy.transactions import app as transactions_app

SQLModel.metadata.create_all(engine)

app = Typer(
    help="An itsy bitsy CLI budgeting assistant.",
    no_args_is_help=True,
)

app.add_typer(transactions_app, name="transactions")
app.add_typer(budgets_app, name="budgets")
app.add_typer(report_app, name="report")


@app.callback()
def callback():
    """An itsy bitsy CLI budgeting assistant."""
    ...


if __name__ == "__main__":
    app()
