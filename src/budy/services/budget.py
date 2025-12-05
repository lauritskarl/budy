import calendar
from collections import defaultdict
from collections.abc import Callable
from datetime import date
from statistics import mean, median

from sqlmodel import Session, asc, select

from budy.models import Budget, Transaction


def get_budgets(
    session: Session,
    target_year: int,
    offset: int,
    limit: int,
) -> list[tuple[int, Budget | None]]:
    """Fetches budgets for a given year, with pagination."""
    budgets = list(
        session.exec(
            select(Budget)
            .where(Budget.target_year == target_year)
            .order_by(asc(Budget.target_month))
            .offset(offset)
            .limit(limit)
        ).all()
    )

    budget_map = {b.target_month: b for b in budgets}

    all_months_data = [(month, budget_map.get(month)) for month in range(1, 13)]

    return all_months_data[offset : offset + limit]


def add_or_update_budget(
    session: Session,
    target_amount: float,
    target_month: int,
    target_year: int,
    confirmation_callback: Callable[[str], bool],
) -> dict:
    """Add a new budget or update an existing one after confirmation."""
    month_name = calendar.month_name[target_month]
    target_cents = int(round(target_amount * 100))

    existing_budget = session.exec(
        select(Budget).where(
            Budget.target_year == target_year,
            Budget.target_month == target_month,
        )
    ).first()

    if existing_budget:
        old_amount = existing_budget.amount
        if not confirmation_callback(
            f"A budget for {month_name} {target_year} already exists. Overwrite?"
        ):
            return {"action": "cancelled"}

        existing_budget.amount = target_cents
        session.add(existing_budget)
        session.commit()
        return {
            "action": "updated",
            "old_amount": old_amount,
            "new_amount": target_cents,
            "month_name": month_name,
            "year": target_year,
        }

    new_budget = Budget(
        amount=target_cents,
        target_month=target_month,
        target_year=target_year,
    )
    session.add(new_budget)
    session.commit()
    return {
        "action": "created",
        "new_amount": target_cents,
        "month_name": month_name,
        "year": target_year,
    }


def generate_budgets_suggestions(
    session: Session,
    target_year: int,
    force: bool,
) -> list[dict]:
    """
    Generates budget suggestions for a given year based on historical data.
    """
    existing_budgets = session.exec(
        select(Budget).where(Budget.target_year == target_year)
    ).all()

    existing_map = {b.target_month: b for b in existing_budgets}

    return [
        {
            "month": month,
            "month_name": calendar.month_name[month],
            "amount": suggested_amount,
            "existing": existing_map.get(month),
        }
        for month in range(1, 13)
        if force or month not in existing_map
        if (suggested_amount := suggest_budget_amount(session, month, target_year)) > 0
    ]


def save_budget_suggestions(
    session: Session,
    suggestions: list[dict],
) -> int:
    """Saves a list of budget suggestions to the database."""
    new_budgets = []

    for item in suggestions:
        if budget := item.get("existing"):
            budget.amount = item["amount"]
        else:
            new_budgets.append(
                Budget(
                    target_year=item["year"],
                    target_month=item["month"],
                    amount=item["amount"],
                )
            )

    if new_budgets:
        session.add_all(new_budgets)

    session.commit()
    return len(suggestions)


def suggest_budget_amount(
    session: Session,
    target_month: int,
    target_year: int,
) -> int:
    """
    Calculates a suggested budget amount (in cents) based on historical data.
    Algorithm: Average of (Median of Recent Trend) and (Median of Historical Seasonality).
    """
    target_date = date(target_year, target_month, 1)

    # 1. Recent Trend: Look at the last 6 months
    # We go back ~180 days. A simple approximation is fine here.
    trend_start = date(target_year, target_month, 1)  # Placeholder
    # Logic to subtract 6 months
    y, m = target_year, target_month
    for _ in range(6):
        m -= 1
        if m < 1:
            m = 12
            y -= 1
    trend_start = date(y, m, 1)

    recent_data = get_monthly_totals(session, trend_start, target_date)
    recent_values = list(recent_data.values())

    # 2. Seasonality: Look at this exact month in the last 3 years
    history_values = []
    for i in range(1, 4):
        prev_year = target_year - i
        # Get totals for that specific month
        # We construct a range of [1st, 1st of next month)
        m_start = date(prev_year, target_month, 1)
        # simplistic next month calculation
        next_m = target_month + 1
        next_y = prev_year
        if next_m > 12:
            next_m = 1
            next_y += 1
        m_end = date(next_y, next_m, 1)

        totals = get_monthly_totals(session, m_start, m_end)
        if totals:
            history_values.extend(totals.values())

    signals = []

    if recent_values:
        signals.append(median(recent_values))

    if history_values:
        signals.append(median(history_values))

    if not signals:
        return 0

    # Return the mean of our signals (Trend + Seasonality)
    return int(mean(signals))


def get_monthly_totals(
    session: Session,
    start_date: date,
    end_date: date,
) -> dict[tuple[int, int], int]:
    """Fetche transactions within a range and aggregate them by year, month."""
    transactions = session.exec(
        select(Transaction).where(
            Transaction.entry_date >= start_date,
            Transaction.entry_date < end_date,
        )
    ).all()

    totals = defaultdict(int)
    for t in transactions:
        totals[(t.entry_date.year, t.entry_date.month)] += t.amount

    return totals
