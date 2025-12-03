from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from sqlmodel import Session, asc, col, desc, or_, select

import budy.importers as importers
from budy.database import engine
from budy.models import Transaction


def get_transactions(offset: int, limit: int) -> list[tuple[date, list[Transaction]]]:
    """
    Fetches transactions for a date range determined by offset and limit.
    """
    today = date.today()
    start_date = today - timedelta(days=offset)
    dates_desc = [start_date - timedelta(days=i) for i in range(limit)]
    dates_to_show = sorted(dates_desc)

    if not dates_to_show:
        return []

    min_date = dates_to_show[0]
    max_date = dates_to_show[-1]

    with Session(engine) as session:
        transactions = list(
            session.exec(
                select(Transaction)
                .where(Transaction.entry_date >= min_date)
                .where(Transaction.entry_date <= max_date)
                .order_by(asc(Transaction.entry_date))
            ).all()
        )

        tx_map = defaultdict(list)
        for t in transactions:
            tx_map[t.entry_date].append(t)

        display_data = []
        for d in dates_to_show:
            display_data.append((d, tx_map.get(d, [])))

        return display_data


def create_transaction(amount: float, entry_date: date | None) -> Transaction:
    """
    Creates and saves a new transaction.
    """
    with Session(engine) as session:
        final_date = entry_date if entry_date else date.today()
        amount_cents = int(round(amount * 100))
        transaction = Transaction(amount=amount_cents, entry_date=final_date)
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction


def import_transactions(bank: str, file_path: Path, dry_run: bool) -> dict:
    """
    Imports transactions from a bank CSV file.
    """
    if bank.lower() == "lhv":
        importer = importers.LHVImporter()
    elif bank.lower() == "seb":
        importer = importers.SEBImporter()
    elif bank.lower() == "swedbank":
        importer = importers.SwedbankImporter()
    else:
        raise ValueError(f"No importer found for {bank}")

    transactions = importer.process_file(file_path)

    if not dry_run and transactions:
        with Session(engine) as session:
            session.add_all(transactions)
            session.commit()
            for t in transactions:
                session.refresh(t)

    return {"transactions": transactions, "count": len(transactions)}


def search_transactions(query: str, limit: int) -> list[Transaction]:
    """
    Searches for transactions by a keyword in the receiver or description.
    """
    with Session(engine) as session:
        pattern = f"%{query}%"
        stmt = (
            select(Transaction)
            .where(
                or_(
                    col(Transaction.receiver).ilike(pattern),
                    col(Transaction.description).ilike(pattern),
                )
            )
            .order_by(desc(Transaction.entry_date))
            .limit(limit)
        )
        return list(session.exec(stmt).all())
