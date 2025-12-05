import calendar
import statistics
from collections import defaultdict
from datetime import date
from statistics import mean
from typing import Optional

from sqlmodel import Session, desc, func, select

from budy.dtos import (
    ForecastData,
    MonthlyReportData,
    PayeeRankingItem,
    VolatilityReportData,
    WeekdayReportItem,
)
from budy.models import Budget, Transaction


def generate_monthly_report_data(
    *,
    session: Session,
    target_month: int,
    target_year: int,
) -> MonthlyReportData:
    """Generates data for the monthly budget status report."""
    today = date.today()
    month_name = calendar.month_name[target_month]
    _, last_day = calendar.monthrange(target_year, target_month)
    start_date = date(target_year, target_month, 1)
    end_date = date(target_year, target_month, last_day)

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

    forecast = None
    is_current_month = (target_month == today.month) and (target_year == today.year)

    if is_current_month:
        days_passed = today.day if today.day > 0 else 1
        avg_per_day = total_spent / days_passed
        projected_total = avg_per_day * last_day
        projected_overage = (projected_total - budget.amount) if budget else None
        forecast = ForecastData(
            avg_per_day=avg_per_day,
            projected_total=projected_total,
            projected_overage=projected_overage,
        )

    return MonthlyReportData(
        budget=budget,
        total_spent=total_spent,
        month_name=month_name,
        target_year=target_year,
        forecast=forecast,
    )


def get_top_payees(
    *,
    session: Session,
    year: int | None,
    limit: int,
    by_count: bool = False,
) -> list[PayeeRankingItem]:
    """Ranks payees by total spending or transaction count."""
    query = select(Transaction)
    if year:
        query = query.where(
            Transaction.entry_date >= date(year, 1, 1),
            Transaction.entry_date <= date(year, 12, 31),
        )

    transactions = session.exec(query).all()
    if not transactions:
        return []

    grouped = defaultdict(list)
    for t in transactions:
        name = (t.receiver or "Unknown").strip() or "Unknown"
        grouped[name].append(t.amount)

    summary = []
    for name, amounts in grouped.items():
        total = sum(amounts)
        count = len(amounts)
        avg = int(total / count)
        summary.append(PayeeRankingItem(name=name, count=count, total=total, avg=avg))

    key_attr = "count" if by_count else "total"
    summary.sort(key=lambda x: getattr(x, key_attr), reverse=True)
    return summary[:limit]


def get_volatility_report_data(
    *, session: Session, year: int | None
) -> Optional[VolatilityReportData]:
    """Calculates spending volatility and identifies outliers."""
    query = select(Transaction)
    if year:
        query = query.where(
            Transaction.entry_date >= date(year, 1, 1),
            Transaction.entry_date <= date(year, 12, 31),
        )

    transactions = session.exec(query.order_by(desc(Transaction.amount))).all()
    if not transactions:
        return None

    amounts = [t.amount for t in transactions]
    try:
        stdev = statistics.stdev(amounts)
    except statistics.StatisticsError:
        stdev = 0

    return VolatilityReportData(
        total_count=len(amounts),
        avg_amount=statistics.mean(amounts),
        stdev_amount=stdev,
        outliers=transactions[:5],
    )


def get_weekday_report_data(*, session: Session) -> list[WeekdayReportItem]:
    """Analyzes spending habits by day of the week."""
    transactions = session.exec(select(Transaction)).all()
    if not transactions:
        return []

    day_buckets = defaultdict(list)
    for t in transactions:
        day_buckets[t.entry_date.weekday()].append(t.amount)

    report_data = []
    for day_idx in range(7):
        amounts = day_buckets[day_idx]
        day_name = calendar.day_name[day_idx]

        if not amounts:
            report_data.append(
                WeekdayReportItem(
                    day_name=day_name, avg_amount=0, total_amount=0, count=0
                )
            )
            continue

        report_data.append(
            WeekdayReportItem(
                day_name=day_name,
                avg_amount=mean(amounts),
                total_amount=sum(amounts),
                count=len(amounts),
            )
        )
    return report_data


def get_yearly_report_data(*, session: Session, year: int) -> list[MonthlyReportData]:
    """Gathers all data needed for the yearly report."""
    monthly_data = []
    for month in range(1, 13):
        monthly_data.append(
            generate_monthly_report_data(
                session=session, target_month=month, target_year=year
            )
        )
    return monthly_data
