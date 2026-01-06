from typing import Annotated

from rich.console import Console
from sqlmodel import Session
from typer import Argument, Exit, Option, Typer, confirm

from budy.database import engine
from budy.services.category import (
    create_category,
    delete_category,
    get_categories,
)
from budy.views.category import render_category_list
from budy.views.messages import render_error, render_success, render_warning

app = Typer(no_args_is_help=True)
console = Console()


@app.command(name="list")
def list_categories_cmd():
    """List all transaction categories."""
    with Session(engine) as session:
        categories = get_categories(session=session)

    if not categories:
        console.print(render_warning(message="No categories found."))
        return

    console.print(render_category_list(categories))


@app.command(name="add")
def add_category_cmd(
    name: Annotated[str, Argument(help="Name of the category.")],
    color: Annotated[
        str,
        Option(
            "--color", "-c", help="Color for the category (e.g. red, blue, #ff0000)."
        ),
    ] = "white",
):
    """Add a new transaction category."""
    try:
        with Session(engine) as session:
            category = create_category(session=session, name=name, color=color)
        console.print(
            render_success(
                message=f"Added category [bold]{category.name}[/] ({category.color})"
            )
        )
    except Exception as e:
        console.print(render_error(message=f"Error adding category: {e}"))
        raise Exit(1)


@app.command(name="delete")
def delete_category_cmd(
    category_id: Annotated[int, Argument(help="ID of the category to delete.")],
    force: Annotated[
        bool,
        Option(
            "--force",
            "-f",
            help="Force delete without confirmation.",
        ),
    ] = False,
):
    """Delete a transaction category."""
    if not force:
        if not confirm(f"Are you sure you want to delete category #{category_id}?"):
            raise Exit()

    with Session(engine) as session:
        success = delete_category(session=session, category_id=category_id)

    if not success:
        console.print(render_error(message=f"Category #{category_id} not found."))
        raise Exit(1)

    console.print(render_success(message=f"Deleted category [bold]#{category_id}[/]"))
