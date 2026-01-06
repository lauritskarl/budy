from pathlib import Path

import polars as pl
from sqlmodel import Session, col, select

from budy.schemas import Category, Transaction


def export_transactions(
    *, session: Session, output_format: str, output_path: Path
) -> int:
    """
    Exports transactions to a CSV or JSON file.
    Returns the number of exported records.
    """
    # 1. Fetch data
    stmt = select(Transaction, Category.name).outerjoin(
        Category, col(Transaction.category_id) == col(Category.id)
    )
    results = session.exec(stmt).all()

    # 2. Convert to list of dicts
    data = []
    for txn, category_name in results:
        record = txn.model_dump()
        record["category"] = category_name or ""
        # Adjust amount to float for export
        record["amount"] = record["amount"] / 100.0
        data.append(record)

    if not data:
        return 0

    # 3. Create DataFrame
    df = pl.DataFrame(data)

    # 4. Write to file
    output_format = output_format.lower()
    if output_format == "csv":
        df.write_csv(output_path)
    elif output_format == "json":
        df.write_json(output_path)
    else:
        raise ValueError(f"Unsupported format: {output_format}")

    return len(data)
