from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlmodel import SQLModel
from typer import Typer

from budy.budgets import app as budgets_app
from budy.categories import app as categories_app
from budy.database import engine
from budy.reports import app as reports_app
from budy.setup import run_setup
from budy.transactions import app as transactions_app


def _run_migrations():
    """Simple migration logic to add columns if they are missing."""
    try:
        with engine.connect() as conn:
            # Check for category_id in transaction table
            try:
                conn.execute(text("SELECT category_id FROM 'transaction' LIMIT 1"))
            except OperationalError as e:
                # Check if it's a missing column error
                if "no such column" in str(e).lower():
                    conn.execute(
                        text(
                            "ALTER TABLE 'transaction' ADD COLUMN category_id INTEGER REFERENCES category(id)"
                        )
                    )
                    conn.commit()
    except Exception:
        # If DB file doesn't exist or other issues, let create_all handle it
        pass


_run_migrations()
SQLModel.metadata.create_all(engine)

app = Typer(no_args_is_help=True)

app.add_typer(transactions_app, name="transactions")
app.add_typer(budgets_app, name="budgets")
app.add_typer(categories_app, name="categories")
app.add_typer(reports_app, name="reports")

app.command(name="setup")(run_setup)


@app.callback()
def callback():
    """An itsy bitsy CLI budgeting assistant."""
    ...


if __name__ == "__main__":
    app()
