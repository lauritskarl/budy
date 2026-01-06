from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from sqlmodel import Session, asc, col, desc, or_, select

from budy.config import settings
from budy.importer import BaseBankImporter
from budy.schemas import Transaction


def get_transactions(
    *,
    session: Session,
    offset: int,
    limit: int,
) -> list[tuple[date, list[Transaction]]]:
    """
    Fetches transactions for a date range by offset and limit, grouped by date.
    """
    today = date.today()

    oldest_date_in_range = today - timedelta(days=offset + limit - 1)
    dates_to_show = [oldest_date_in_range + timedelta(days=i) for i in range(limit)]

    min_date_query = dates_to_show[0]
    max_date_query = dates_to_show[-1]

    transactions = list(
        session.exec(
            select(Transaction)
            .where(Transaction.entry_date >= min_date_query)
            .where(Transaction.entry_date <= max_date_query)
            .order_by(asc(Transaction.entry_date))
        ).all()
    )

    tx_map = defaultdict(list)
    for t in transactions:
        tx_map[t.entry_date].append(t)

    return [(d, tx_map.get(d, [])) for d in dates_to_show]


def create_transaction(
    *,
    session: Session,
    amount: float,
    entry_date: date | None = None,
) -> Transaction:
    """Creates and saves a new transaction."""
    final_date = entry_date or date.today()
    amount_cents = int(round(amount * 100))
    transaction = Transaction(amount=amount_cents, entry_date=final_date)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


def update_transaction(
    *,
    session: Session,
    transaction_id: int,
    amount: float | None = None,
    entry_date: date | None = None,
    receiver: str | None = None,
    description: str | None = None,
) -> Transaction | None:
    """Updates an existing transaction."""
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        return None

    if amount is not None:
        transaction.amount = int(round(amount * 100))
    if entry_date is not None:
        transaction.entry_date = entry_date
    if receiver is not None:
        transaction.receiver = receiver
    if description is not None:
        transaction.description = description

    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


def delete_transaction(*, session: Session, transaction_id: int) -> bool:
    """Deletes a transaction by ID."""
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        return False

    session.delete(transaction)
    session.commit()
    return True


def import_transactions(
    *,
    session: Session,
    bank_name: str,
    file_path: Path,
    dry_run: bool,
) -> list[Transaction]:
    """Imports transactions from a bank CSV file."""
    bank_name_key = bank_name.lower()
    bank_config = settings.banks.get(bank_name_key)

    if not bank_config:
        available = ", ".join(settings.banks.keys())
        raise ValueError(f"Unknown bank '{bank_name}'. Available banks: {available}")

    importer = BaseBankImporter(**bank_config.model_dump())

    transactions = importer.process_file(file_path)

    if not dry_run and transactions:
        session.add_all(transactions)
        session.commit()

    return transactions


def search_transactions(
    *, session: Session, query: str, limit: int
) -> list[Transaction]:
    """Search for transactions by receiver or description keyword."""
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
