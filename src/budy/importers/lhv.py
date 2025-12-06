from .base import BaseBankImporter


class LHVImporter(BaseBankImporter):
    delimiter: str = ","
    encoding: str = "utf-8"
    decimal: str = "."

    date_col: str = "Kuupäev"
    amount_col: str = "Summa"
    debit_credit_col: str = "Deebet/Kreedit (D/C)"
    debit_value: str = "D"

    receiver_col: str = "Saaja/maksja nimi"
    description_col: str = "Selgitus"
