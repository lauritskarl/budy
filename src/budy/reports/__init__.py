from typer import Typer

from .month import app as month_app

app = Typer(no_args_is_help=True)

app.add_typer(month_app)


@app.callback()
def callback():
    """View financial insights."""
    ...
