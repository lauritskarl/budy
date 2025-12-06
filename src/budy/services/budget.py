import calendar
from collections import defaultdict
from datetime import date
from statistics import mean
from typing import Optional

from sqlmodel import Session, asc, select

from budy.constants import MIN_YEAR
from budy.schemas import Budget, BudgetSuggestion, Transaction


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
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder

    start_date = date(MIN_YEAR, 1, 1)
    end_date = date(target_year, target_month, 1)

    historical_data = get_monthly_totals(
        session=session, start_date=start_date, end_date=end_date
    )

    if len(historical_data) < 6:
        return int(mean(historical_data.values())) if historical_data else 0

    # 2. Prepare Training Data (X = [Month, Year], y = Amount)
    X_train = []
    y_train = []

    for (year, month), amount in historical_data.items():
        X_train.append([month, year])
        y_train.append(amount)

    # 3. Build & Train Pipeline
    # We one-hot encode 'Month' so the model understands "December" distinct from "January" independent of the numerical value (1 vs 12).
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), [0]),  # Month column
            ("num", "passthrough", [1]),  # Year column
        ]
    )

    model = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(n_estimators=100, random_state=42)),
        ]
    )

    model.fit(X_train, y_train)

    # 4. Predict
    # Input must match X_train shape: [[target_month, target_year]]
    prediction = model.predict([[target_month, target_year]])

    # Round to nearest 100 currency units (e.g., 100 EUR/USD)
    # Since amount is in cents, 100 currency units is 100 * 100 = 10000 cents
    rounded_prediction = round(prediction[0] / 10000) * 10000

    return int(rounded_prediction)


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
