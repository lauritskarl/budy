from typer import Typer

from .add import app as add_app
from .list import app as list_app

app = Typer(no_args_is_help=True)

app.add_typer(add_app)
app.add_typer(list_app)


@app.callback()
def callback():
    """Set and manage monthly targets."""
    ...
