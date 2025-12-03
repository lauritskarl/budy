import calendar
import statistics
from collections import defaultdict
from datetime import date
from statistics import mean

from sqlmodel import Session, desc, func, select

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


def get_top_payees(
    year: int | None,
    limit: int,
    by_count: bool = False,
) -> list[tuple[str, int, int, int]]:
    """
    Ranks payees by total spending or transaction count for a given year or all time.
    """
    with Session(engine) as session:
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
            name = (t.receiver or "Unknown").strip()
            if not name:
                name = "Unknown"
            grouped[name].append(t.amount)

        summary = []
        for name, amounts in grouped.items():
            total = sum(amounts)
            count = len(amounts)
            avg = int(total / count)
            summary.append((name, count, total, avg))

        # Sort by Count (index 1) if requested, otherwise by Total Amount (index 2)
        sort_index = 1 if by_count else 2
        summary.sort(key=lambda x: x[sort_index], reverse=True)
        return summary[:limit]


def get_volatility_report_data(year: int | None) -> dict:
    """
    Calculates spending volatility and identifies outliers.
    """
    with Session(engine) as session:
        query = select(Transaction)
        if year:
            query = query.where(
                Transaction.entry_date >= date(year, 1, 1),
                Transaction.entry_date <= date(year, 12, 31),
            )

        transactions = session.exec(query.order_by(desc(Transaction.amount))).all()
        if not transactions:
            return {}

        amounts = [t.amount for t in transactions]
        try:
            stdev = statistics.stdev(amounts)
        except statistics.StatisticsError:
            stdev = 0

        return {
            "total_count": len(amounts),
            "avg_amount": statistics.mean(amounts),
            "stdev_amount": stdev,
            "outliers": transactions[:5],
        }


def get_weekday_report_data() -> list[dict]:
    """
    Analyzes spending habits by day of the week.
    """
    with Session(engine) as session:
        transactions = session.exec(select(Transaction)).all()
        if not transactions:
            return []

        day_buckets = defaultdict(list)
        for t in transactions:
            day_buckets[t.entry_date.weekday()].append(t.amount)

        report_data = []
        for day_idx in range(7):
            amounts = day_buckets[day_idx]
            if not amounts:
                report_data.append(
                    {
                        "day_name": calendar.day_name[day_idx],
                        "avg_amount": 0,
                        "total_amount": 0,
                        "count": 0,
                    }
                )
                continue

            report_data.append(
                {
                    "day_name": calendar.day_name[day_idx],
                    "avg_amount": mean(amounts),
                    "total_amount": sum(amounts),
                    "count": len(amounts),
                }
            )
        return report_data


def get_yearly_report_data(year: int) -> list[dict]:
    """
    Gathers all data needed for the yearly report.
    """
    monthly_data = []
    with Session(engine) as session:
        for month in range(1, 13):
            month_name = calendar.month_name[month]
            budget = session.exec(
                select(Budget).where(
                    Budget.target_year == year, Budget.target_month == month
                )
            ).first()

            _, last_day = calendar.monthrange(year, month)
            start_date = date(year, month, 1)
            end_date = date(year, month, last_day)

            total_spent = (
                session.scalar(
                    select(func.sum(Transaction.amount)).where(
                        Transaction.entry_date >= start_date,
                        Transaction.entry_date <= end_date,
                    )
                )
                or 0
            )

            monthly_data.append(
                {
                    "budget": budget,
                    "total_spent": total_spent,
                    "month_name": month_name,
                    "target_year": year,
                }
            )
    return monthly_data
