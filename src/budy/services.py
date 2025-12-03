import calendar
from collections import defaultdict
from datetime import date, timedelta
from statistics import mean, median

from sqlmodel import Session, asc, func, select

from budy.database import engine
from budy.models import Budget, Transaction


def generate_monthly_report_data(target_month: int, target_year: int) -> dict:
    """
    Generates all data needed for the monthly budget status report.
    """
    today = date.today()
    month_name = calendar.month_name[target_month]
    _, last_day = calendar.monthrange(target_year, target_month)
    start_date = date(target_year, target_month, 1)
    end_date = date(target_year, target_month, last_day)

    with Session(engine) as session:
        budget = session.exec(
            select(Budget).where(
                Budget.target_year == target_year,
                Budget.target_month == target_month,
            )
        ).first()

        total_spent = (
            session.scalar(
                select(func.sum(Transaction.amount)).where(
                    Transaction.entry_date >= start_date,
                    Transaction.entry_date <= end_date,
                )
            )
            or 0
        )

    report_data = {
        "budget": budget,
        "total_spent": total_spent,
        "month_name": month_name,
        "target_year": target_year,
        "forecast": None,
    }

    is_current_month = (target_month == today.month) and (target_year == today.year)
    if is_current_month:
        days_passed = today.day
        if days_passed == 0:
            days_passed = 1

        avg_per_day = total_spent / days_passed
        projected_total = avg_per_day * last_day
        projected_overage = (projected_total - budget.amount) if budget else None

        report_data["forecast"] = {
            "avg_per_day": avg_per_day,
            "projected_total": projected_total,
            "projected_overage": projected_overage,
        }

    return report_data


def get_budgets(
    target_year: int, offset: int, limit: int
) -> list[tuple[int, Budget | None]]:
    """
    Fetches budgets for a given year, with optional pagination.
    """
    with Session(engine) as session:
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
        all_months_data = []

        for month in range(1, 13):
            all_months_data.append((month, budget_map.get(month)))

        return all_months_data[offset : offset + limit]


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
