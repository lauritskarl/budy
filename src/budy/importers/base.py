from pathlib import Path
from typing import Optional

from sqlmodel import SQLModel

from budy.schemas import Transaction


class BaseBankImporter(SQLModel):
    delimiter: str = ","
    encoding: str = "utf-8"
    decimal: str = "."

    # Required columns for core functionality
    date_col: str
    amount_col: str
    debit_credit_col: str
    debit_value: str = "D"

    # Optional columns for richer data
    receiver_col: Optional[str] = None
    description_col: Optional[str] = None

    def process_file(self, file_path: Path) -> list[Transaction]:
        import polars as pl

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            df = pl.read_csv(
                file_path,
                separator=self.delimiter,
                decimal_comma=(self.decimal == ","),
                encoding=self.encoding,
                infer_schema_length=10000,
            )

            required_cols = {self.date_col, self.amount_col, self.debit_credit_col}

            if not required_cols.issubset(df.columns):
                missing = required_cols - set(df.columns)
                raise ValueError(f"CSV missing required columns: {missing}")

            # Start building the lazy query
            q = df.lazy().filter(
                pl.col(self.debit_credit_col).str.strip_chars().str.to_uppercase()
                == self.debit_value
            )

            # 1. Parse Date
            q = q.with_columns(
                pl.col(self.date_col)
                .str.strptime(pl.Date, strict=False)
                .alias("parsed_date")
            )

            # 2. Parse Amount (handle cents)
            q = q.with_columns(
                (pl.col(self.amount_col).abs() * 100)
                .round()
                .cast(pl.Int64)
                .alias("amount_cents")
            )

            # 3. Parse Receiver (Optional)
            if self.receiver_col and self.receiver_col in df.columns:
                q = q.with_columns(
                    pl.col(self.receiver_col).fill_null("").alias("receiver_val")
                )
            else:
                q = q.with_columns(pl.lit(None).cast(pl.String).alias("receiver_val"))

            # 4. Parse Description (Optional)
            if self.description_col and self.description_col in df.columns:
                q = q.with_columns(
                    pl.col(self.description_col).fill_null("").alias("desc_val")
                )
            else:
                q = q.with_columns(pl.lit(None).cast(pl.String).alias("desc_val"))

            # Final Selection
            result = (
                q.drop_nulls(subset=["parsed_date", "amount_cents"])
                .filter(pl.col("amount_cents") > 0)
                .select(["parsed_date", "amount_cents", "receiver_val", "desc_val"])
            ).collect()

            return [
                Transaction(
                    entry_date=row["parsed_date"],
                    amount=row["amount_cents"],
                    receiver=row["receiver_val"] or None,
                    description=row["desc_val"] or None,
                )
                for row in result.to_dicts()
            ]

        except Exception as e:
            raise RuntimeError(f"Error parsing CSV: {e}") from e
