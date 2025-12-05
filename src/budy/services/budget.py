import calendar
from collections import defaultdict
from datetime import date
from statistics import mean, median
from typing import Optional

from sqlmodel import Session, asc, select

from budy.dtos import BudgetSuggestion
from budy.models import Budget, Transaction


def get_budget(
    *,
    session: Session,
    target_month: int,
    target_year: int,
) -> Optional[Budget]:
    """Retrieves a specific budget if it exists."""
    return session.exec(
        select(Budget).where(
            Budget.target_year == target_year,
            Budget.target_month == target_month,
        )
    ).first()


def upsert_budget(
    *,
    session: Session,
    amount: float,
    target_month: int,
    target_year: int,
) -> Budget:
    """Creates or updates a budget."""
    target_cents = int(round(amount * 100))
    budget = get_budget(
        session=session,
        target_month=target_month,
        target_year=target_year,
    )

    if budget:
        budget.amount = target_cents
    else:
        budget = Budget(
            amount=target_cents,
            target_month=target_month,
            target_year=target_year,
        )

    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


def get_budgets(
    *,
    session: Session,
    target_year: int,
    offset: int,
    limit: int,
) -> list[tuple[int, Budget | None]]:
    """Fetches budgets for a given year with optional pagination."""
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


def generate_budgets_suggestions(
    *,
    session: Session,
    target_year: int,
    force: bool,
) -> list[BudgetSuggestion]:
    """Generates budget suggestions for a given year based on historical data."""
    existing_budgets = session.exec(
        select(Budget).where(Budget.target_year == target_year)
    ).all()

    existing_map = {b.target_month: b for b in existing_budgets}
    suggestions = []

    for month in range(1, 13):
        if not force and month in existing_map:
            continue

        suggested_amount = suggest_budget_amount(
            session=session, target_month=month, target_year=target_year
        )
        if suggested_amount > 0:
            suggestions.append(
                BudgetSuggestion(
                    month=month,
                    month_name=calendar.month_name[month],
                    amount=suggested_amount,
                    year=target_year,
                    existing=existing_map.get(month),
                )
            )

    return suggestions


def save_budget_suggestions(
    *,
    session: Session,
    suggestions: list[BudgetSuggestion],
) -> int:
    """Saves a list of budget suggestions to the database."""
    for item in suggestions:
        if item.existing:
            item.existing.amount = item.amount
            session.add(item.existing)
        else:
            session.add(
                Budget(
                    target_year=item.year,
                    target_month=item.month,
                    amount=item.amount,
                )
            )

    session.commit()
    return len(suggestions)


def suggest_budget_amount(
    *,
    session: Session,
    target_month: int,
    target_year: int,
) -> int:
    """Calculates a suggested budget amount (in cents) based on historical data."""
    target_date = date(target_year, target_month, 1)

    # 1. Recent Trend: Look back ~6 months
    y, m = target_year, target_month
    for _ in range(6):
        m -= 1
        if m < 1:
            m = 12
            y -= 1
    trend_start = date(y, m, 1)

    recent_data = get_monthly_totals(
        session=session, start_date=trend_start, end_date=target_date
    )
    recent_values = list(recent_data.values())

    # 2. Seasonality: Look at this exact month in the last 3 years
    history_values = []
    for i in range(1, 4):
        prev_year = target_year - i
        m_start = date(prev_year, target_month, 1)
        next_m = target_month + 1
        next_y = prev_year
        if next_m > 12:
            next_m = 1
            next_y += 1
        m_end = date(next_y, next_m, 1)

        totals = get_monthly_totals(session=session, start_date=m_start, end_date=m_end)
        if totals:
            history_values.extend(totals.values())

    signals = []
    if recent_values:
        signals.append(median(recent_values))
    if history_values:
        signals.append(median(history_values))

    if not signals:
        return 0

    return int(mean(signals))


def get_monthly_totals(
    *,
    session: Session,
    start_date: date,
    end_date: date,
) -> dict[tuple[int, int], int]:
    """Fetches transactions within a range and aggregates them by year, month."""
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
