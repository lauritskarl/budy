from rich.table import Table


def render_payee_ranking(payees: list[tuple[str, int, int, int]]) -> Table:
    """
    Renders a ranking table of payees.
    Data format: (Receiver Name, Transaction Count, Total Amount, Average Amount)
    """
    table = Table(title="Top Payees", show_footer=False)
    table.add_column("Rank", style="dim", justify="right")
    table.add_column("Payee", style="cyan bold")
    table.add_column("Count", justify="right", style="white")
    table.add_column("Total", justify="right", style="green")
    table.add_column("Avg", justify="right", style="dim")

    for i, (name, count, total, avg) in enumerate(payees, 1):
        table.add_row(
            f"#{i}",
            name,
            str(count),
            f"${total / 100:,.2f}",
            f"${avg / 100:,.2f}",
        )

    return table
