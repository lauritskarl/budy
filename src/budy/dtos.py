from dataclasses import dataclass
from typing import Optional

from budy.models import Budget, Transaction


@dataclass
class ForecastData:
    avg_per_day: float
    projected_total: float
    projected_overage: float | None


@dataclass
class MonthlyReportData:
    budget: Budget | None
    total_spent: int
    month_name: str
    target_year: int
    forecast: Optional[ForecastData] = None


@dataclass
class VolatilityReportData:
    total_count: int
    avg_amount: float
    stdev_amount: float
    outliers: list[Transaction]


@dataclass
class WeekdayReportItem:
    day_name: str
    avg_amount: float
    total_amount: int
    count: int


@dataclass
class PayeeRankingItem:
    name: str
    count: int
    total: int
    avg: int


@dataclass
class BudgetSuggestion:
    month: int
    month_name: str
    amount: int
    year: int
    existing: Optional[Budget] = None
