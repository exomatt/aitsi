from typing import List

import pandas as pd


class UsesTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame()
        self.table: pd.DataFrame = table

    def set_uses(self, var_name: str, stmt: str) -> None:
        if stmt not in self.table.columns.tolist():
            self.table[stmt] = 0
        if var_name not in self.table.index.tolist():
            self.table.loc[var_name] = 0
        self.table.loc[var_name, stmt] = 1

    def set_uses_from_procedure(self, called_from: str, called_to: str) -> None:
        try:
            self.table.loc[self.table[called_to] == 1, called_from] = 1
        except Exception:
            pass

    def get_used(self, stmt: str) -> List[str]:
        try:
            return self.table.index[self.table[str(stmt)] == 1].tolist()
        except Exception:
            return []

    def get_uses(self, var_name: str) -> List[str]:
        try:
            return self.table.columns[self.table.loc[var_name] == 1].tolist()
        except Exception:
            return []

    def is_used(self, stmt: str, var_name: str) -> bool:
        try:
            return bool(self.table.at[var_name, stmt])
        except Exception:
            return False

    def to_string(self) -> None:
        print("UsesTable:")
        print(self.table.to_string())

    def to_log(self) -> str:
        return "UsesTable: \n" + self.table.to_string()
