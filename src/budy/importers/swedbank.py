from .base import BaseBankImporter


class SwedbankImporter(BaseBankImporter):
    delimiter: str = ";"
    encoding: str = "utf-8"
    decimal: str = ","

    date_col: str = "Kuupäev"
    amount_col: str = "Summa"
    debit_credit_col: str = "Deebet/Kreedit"
    debit_value: str = "D"

    receiver_col: str = "Saaja/Maksja"
    description_col: str = "Selgitus"
