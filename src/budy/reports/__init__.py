from typer import Typer

from .month import app as month_app
from .search import app as search_app
from .top_payees import app as top_payees_app
from .volatility import app as volatility_app
from .weekday import app as weekday_app
from .year import app as year_app

app = Typer(no_args_is_help=True)

app.add_typer(month_app)
app.add_typer(year_app)
app.add_typer(weekday_app)
app.add_typer(volatility_app)
app.add_typer(search_app)
app.add_typer(top_payees_app)


@app.callback()
def callback():
    """View financial insights."""
    ...
