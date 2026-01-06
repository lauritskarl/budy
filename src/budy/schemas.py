from datetime import date

from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    """Class that defines transaction categories."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    color: str = Field(default="white")


class Transaction(SQLModel, table=True):
    """Class that defines all transactions."""

    id: int | None = Field(default=None, primary_key=True)
    amount: int
    entry_date: date = Field(index=True)
    receiver: str | None = Field(default=None, index=True)
    description: str | None = Field(default=None)
    category_id: int | None = Field(default=None, foreign_key="category.id")


class Budget(SQLModel, table=True):
    """Class that defines all budgets."""

    id: int | None = Field(default=None, primary_key=True)
    amount: int
    target_month: int = Field(index=True)
    target_year: int = Field(index=True)


class ForecastData(SQLModel):
    """Represents forecast data for budgeting."""

    avg_per_day: float
    projected_total: float
    projected_overage: float | None


class MonthlyReportData(SQLModel):
    """Represents monthly report data, including budget and spending."""

    budget: Budget | None
    total_spent: int
    month_name: str
    target_year: int
    forecast: ForecastData | None = None


class VolatilityReportData(SQLModel):
    """Represents data for a volatility report, including outliers."""

    total_count: int
    avg_amount: float
    stdev_amount: float
    outliers: list[Transaction]


class WeekdayReportItem(SQLModel):
    """Represents a single item in a weekday spending report."""

    day_name: str
    avg_amount: float
    total_amount: int
    count: int


class PayeeRankingItem(SQLModel):
    """Represents a single item in a payee ranking report."""

    name: str
    count: int
    total: int
    avg: int


class BudgetSuggestion(SQLModel):
    """Represents a budget suggestion for a specific month."""

    month: int
    month_name: str
    amount: int
    year: int
    existing: Budget | None = None
