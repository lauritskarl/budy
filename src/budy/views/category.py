from rich.table import Table

from budy.schemas import Category


def render_category_list(categories: list[Category]) -> Table:
    """Renders a list of categories in a table."""
    table = Table(title="Transaction Categories")

    table.add_column("ID", style="dim", width=4)
    table.add_column("Name", style="bold")
    table.add_column("Color")

    for cat in categories:
        color_style = cat.color if cat.color else "white"
        table.add_row(
            str(cat.id),
            cat.name,
            f"[{color_style}]■[/] {cat.color}",
        )

    return table
