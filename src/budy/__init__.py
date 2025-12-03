from sqlmodel import SQLModel
from typer import Typer

from budy.budgets import app as budgets_app
from budy.database import engine
from budy.reports import app as reports_app
from budy.transactions import app as transactions_app

SQLModel.metadata.create_all(engine)

app = Typer(no_args_is_help=True)

app.add_typer(transactions_app, name="transactions")
app.add_typer(transactions_app, name="t", hidden=True)
app.add_typer(budgets_app, name="budgets")
app.add_typer(budgets_app, name="b", hidden=True)
app.add_typer(reports_app, name="reports")
app.add_typer(reports_app, name="r", hidden=True)


@app.callback()
def callback():
    """An itsy bitsy CLI budgeting assistant."""
    ...


if __name__ == "__main__":
    app()
