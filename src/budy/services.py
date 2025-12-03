from collections import defaultdict
from datetime import date
from statistics import mean, median

from sqlmodel import Session, select

from budy.models import Transaction


def get_monthly_totals(
    session: Session, start_date: date, end_date: date
) -> dict[tuple[int, int], int]:
    """
    Fetches transactions within a range and aggregates them by (year, month).
    Returns a dict: {(year, month): total_cents}
    """
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


def suggest_budget_amount(session: Session, target_month: int, target_year: int) -> int:
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
