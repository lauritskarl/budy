import csv
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from sqlmodel import SQLModel

from budy.models import Transaction


def get_bank_importers() -> dict[str, type["BaseBankImporter"]]:
    """
    Dynamically discover all BaseBankImporter subclasses.
    Returns a dict mapping 'bank_name' -> ImporterClass.
    """
    banks = {}
    for cls in BaseBankImporter.__subclasses__():
        name = cls.__name__.replace("Importer", "").lower()
        banks[name] = cls
    return banks


class ImportResult(SQLModel):
    success: bool
    count: int = 0
    message: str = ""
    error: Optional[str] = None


class BaseBankImporter(SQLModel):
    """
    Base configuration and logic for parsing bank CSVs.
    Subclasses should define the specific column names and formats as fields.
    """

    delimiter: str = ","
    encoding: str = "utf-8"
    decimal: str = "."
    date_fmt: Optional[str] = None
    debit_value: str = "D"

    date_col: str
    amount_col: str
    debit_credit_col: str

    def _parse_amount(self, amount_str: str) -> Optional[int]:
        """Parses an amount string to cents."""
        try:
            if self.decimal != ".":
                amount_str = amount_str.replace(self.decimal, ".")

            amount = float(amount_str)
            return int(round(abs(amount) * 100))
        except (ValueError, TypeError):
            return None

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parses a date string into a date object."""
        try:
            if self.date_fmt:
                return datetime.strptime(date_str, self.date_fmt).date()

            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                try:
                    return datetime.strptime(date_str, "%d.%m.%Y").date()
                except ValueError:
                    return None
        except (ValueError, TypeError):
            return None

    def _parse_row(self, row: dict[str, str]) -> Optional[Transaction]:
        """Parses a single CSV row into a Transaction."""
        required = [self.date_col, self.amount_col, self.debit_credit_col]
        if not all(col in row for col in required):
            return None

        date_obj = self._parse_date(row[self.date_col])
        amount_cents = self._parse_amount(row[self.amount_col])
        debit_credit_indicator = row[self.debit_credit_col].strip().upper()

        if date_obj is None or amount_cents is None:
            return None

        is_expense = debit_credit_indicator == self.debit_value.strip().upper()

        if not is_expense or amount_cents <= 0:
            return None

        return Transaction(entry_date=date_obj, amount=amount_cents)

    def process_file(self, file_path: Path) -> tuple[list[Transaction], ImportResult]:
        """Reads the CSV and returns valid Transactions."""
        transactions: list[Transaction] = []

        if not file_path.exists():
            return [], ImportResult(
                success=False, message=f"File not found: {file_path}"
            )

        try:
            with open(
                file_path,
                mode="r",
                encoding=self.encoding,
                newline="",
            ) as f:
                reader = csv.DictReader(f, delimiter=self.delimiter)
                header = reader.fieldnames

                required_cols = {self.date_col, self.amount_col, self.debit_credit_col}

                if header is None or not required_cols.issubset(header):
                    missing = required_cols - set(header if header else [])
                    return [], ImportResult(
                        success=False,
                        message="CSV missing required columns.",
                        error=f"Missing columns: {missing}",
                    )

                for row in reader:
                    transaction = self._parse_row(row)
                    if transaction:
                        transactions.append(transaction)

            if not transactions:
                return [], ImportResult(
                    success=True,
                    count=0,
                    message=f"No valid expenses found in {file_path.name}.",
                )

            return transactions, ImportResult(
                success=True,
                count=len(transactions),
                message=f"Parsed {len(transactions)} transactions.",
            )

        except Exception as e:
            return [], ImportResult(
                success=False, message="Error reading CSV", error=str(e)
            )


class LHVImporter(BaseBankImporter):
    date_col: str = "Kuupäev"
    date_fmt: str = "%Y-%m-%d"
    debit_credit_col: str = "Deebet/Kreedit (D/C)"
    amount_col: str = "Summa"


class SEBImporter(BaseBankImporter):
    delimiter: str = ";"
    decimal: str = ","
    date_col: str = "Kuupäev"
    date_fmt: str = "%d.%m.%Y"
    debit_credit_col: str = "Deebet/Kreedit (D/C)"
    amount_col: str = "Summa"


class SwedbankImporter(BaseBankImporter):
    delimiter: str = ";"
    decimal: str = ","
    date_col: str = "Kuupäev"
    date_fmt: str = "%d.%m.%Y"
    debit_credit_col: str = "Deebet/Kreedit"
    amount_col: str = "Summa"
