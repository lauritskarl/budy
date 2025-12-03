from pathlib import Path
from typing import Optional

import pandas as pd
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
    delimiter: str = ","
    encoding: str = "utf-8"
    decimal: str = "."
    dayfirst: bool = False

    date_col: str
    amount_col: str
    debit_credit_col: str
    debit_value: str = "D"

    def process_file(self, file_path: Path) -> tuple[list[Transaction], ImportResult]:
        if not file_path.exists():
            return [], ImportResult(success=False, message="File not found")

        try:
            # 1. READ & PARSE (Handling delimiters, decimals, and dates in one go)
            df = pd.read_csv(
                file_path,
                sep=self.delimiter,
                decimal=self.decimal,
                encoding=self.encoding,
                parse_dates=[self.date_col],
                dayfirst=self.dayfirst,  # True for European dates like 31.01.2023
            )

            # 2. FILTER (Keep only Debits/Expenses)
            # Normalize column to string/upper just in case
            df[self.debit_credit_col] = (
                df[self.debit_credit_col].astype(str).str.strip().str.upper()
            )
            df = df[df[self.debit_credit_col] == self.debit_value]

            # 3. CLEAN UP
            # Ensure amounts are positive (if they aren't already)
            df[self.amount_col] = df[self.amount_col].abs()
            # Drop rows with invalid dates or 0 amounts
            df = df.dropna(subset=[self.date_col, self.amount_col])
            df = df[df[self.amount_col] > 0]

            # 4. CONVERT TO MODEL
            transactions = []
            for _, row in df.iterrows():
                transactions.append(
                    Transaction(
                        entry_date=row[self.date_col].date(),
                        # Convert float dollars to integer cents
                        amount=int(round(row[self.amount_col] * 100)),
                    )
                )

            return transactions, ImportResult(
                success=True,
                count=len(transactions),
                message=f"Parsed {len(transactions)} transactions.",
            )

        except Exception as e:
            return [], ImportResult(
                success=False, message="Error parsing CSV", error=str(e)
            )


class LHVImporter(BaseBankImporter):
    delimiter: str = ","
    encoding: str = "utf-8"
    decimal: str = "."
    dayfirst: bool = False
    date_col: str = "Kuupäev"
    amount_col: str = "Summa"
    debit_credit_col: str = "Deebet/Kreedit (D/C)"
    debit_value: str = "D"


class SEBImporter(BaseBankImporter):
    delimiter: str = ";"
    encoding: str = "utf-8"
    decimal: str = ","
    dayfirst: bool = True
    date_col: str = "Kuupäev"
    amount_col: str = "Summa"
    debit_credit_col: str = "Deebet/Kreedit (D/C)"
    debit_value: str = "D"


class SwedbankImporter(BaseBankImporter):
    delimiter: str = ";"
    encoding: str = "utf-8"
    decimal: str = ","
    dayfirst: bool = True
    date_col: str = "Kuupäev"
    amount_col: str = "Summa"
    debit_credit_col: str = "Deebet/Kreedit"
    debit_value: str = "D"
