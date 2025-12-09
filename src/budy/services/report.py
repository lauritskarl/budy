import calendar
import statistics
from collections import defaultdict
from datetime import date
from statistics import mean
from typing import Optional

from sqlmodel import Session, desc, select

from budy.config import settings
from budy.schemas import (
    Budget,
    ForecastData,
    MonthlyReportData,
    PayeeRankingItem,
    Transaction,
    VolatilityReportData,
    WeekdayReportItem,
)


def _get_name_variants(name: str) -> set[str]:
    """Generates variants of a name (lowercase, initials, mixed forms)."""
    clean_name = name.strip().lower()
    parts = clean_name.split()

    if not parts:
        return {clean_name}

    variants = {clean_name}

    # 1. All Initials (e.g. "khl", "k.h.l.", "k. h. l.")
    initials_chars = [p[0] for p in parts]
    variants.add("".join(initials_chars))
    variants.add(".".join(initials_chars) + ".")
    variants.add(". ".join(initials_chars) + ".")

    if len(parts) > 1:
        last_name = parts[-1]
        first_names = parts[:-1]
        first_initials_chars = [p[0] for p in first_names]

        # 2. First name initial + Last name full (e.g. "k laurits", "k. laurits")
        first_initial = first_names[0][0]
        variants.add(f"{first_initial} {last_name}")
        variants.add(f"{first_initial}. {last_name}")
        variants.add(f"{first_initial}.{last_name}")

        # 3. All first names initialed + Last name full (e.g. "k. h. laurits")
        if len(first_names) > 1:
            # "kh laurits"
            variants.add(f"{''.join(first_initials_chars)} {last_name}")
            # "k. h. laurits"
            dotted_spaced = ". ".join(first_initials_chars) + "."
            variants.add(f"{dotted_spaced} {last_name}")
            # "k.h. laurits"
            dotted_tight = ".".join(first_initials_chars) + "."
            variants.add(f"{dotted_tight} {last_name}")

    return variants


def _is_user(receiver: str | None) -> bool:
    """Checks if the receiver matches the configured user (fuzzy match)."""
    if not receiver:
        return False

    if not settings.first_name or not settings.last_name:
        return False

    receiver_clean = receiver.strip().lower()
    full_name = f"{settings.first_name} {settings.last_name}"

    user_variants = _get_name_variants(full_name)
    if receiver_clean in user_variants:
        return True

    receiver_variants = _get_name_variants(receiver)
    if full_name.lower() in receiver_variants:
        return True

    return False


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

    transactions = session.exec(
        select(Transaction).where(
            Transaction.entry_date >= start_date,
            Transaction.entry_date <= end_date,
        )
    ).all()

    relevant_transactions = [t for t in transactions if not _is_user(t.receiver)]

    total_spent = sum(t.amount for t in relevant_transactions)

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

    filtered_transactions = [t for t in transactions if not _is_user(t.receiver)]

    grouped = defaultdict(list)
    for t in filtered_transactions:
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

    transactions = [t for t in transactions if not _is_user(t.receiver)]

    if not transactions or len(transactions) < 10:
        return None

    amounts = [t.amount for t in transactions]
    avg_amount = statistics.mean(amounts)

    try:
        stdev = statistics.stdev(amounts)
    except statistics.StatisticsError:
        stdev = 0

    # Statistical Outlier Detection (Z-Score method)
    # We flag transactions that are more than 2 standard deviations above the mean.
    threshold = avg_amount + (2 * stdev)

    outliers = [t for t in transactions if t.amount > threshold]
    # Sort purely by amount for the report
    outliers.sort(key=lambda t: t.amount, reverse=True)

    return VolatilityReportData(
        total_count=len(amounts),
        avg_amount=avg_amount,
        stdev_amount=stdev,
        outliers=outliers[:5],
    )


def get_weekday_report_data(*, session: Session) -> list[WeekdayReportItem]:
    """Analyzes spending habits by day of the week."""
    transactions = session.exec(select(Transaction)).all()

    transactions = [t for t in transactions if not _is_user(t.receiver)]

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
