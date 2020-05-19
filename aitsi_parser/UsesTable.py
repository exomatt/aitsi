from typing import List

import pandas as pd


class UsesTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame()
        self.table: pd.DataFrame = table

    def set_uses(self, var_name: str, stmt: str) -> None:
        if var_name not in self.table.index[:]:
            indexes: List[str] = list(self.table.index[:])
            indexes.append(var_name)
            self.table = self.table.reindex(indexes)
            self.table = self.table.sort_index(axis=0)
        if stmt not in self.table.columns.values:
            self.table[stmt] = pd.Series(1, index=[var_name])
            self.table = self.table.sort_index(axis=1)
            self.table = self.table.fillna(value=0)
        else:
            self.table = self.table.fillna(value=0)
            self.table[stmt][var_name] = 1

    def get_used(self, stmt: str) -> List[str]:
        try:
            return self.table.index[self.table[stmt] == 1].tolist()
        except Exception:
            return []

    def get_uses(self, var_name: str) -> List[str]:
        try:
            return self.table.columns[self.table.loc[var_name] == 1].tolist()
        except Exception:
            return []

    def is_used(self, var_name: str, stmt: str) -> bool:
        try:
            return bool(self.table.at[var_name, stmt])
        except Exception:
            return False

    def to_string(self) -> None:
        print("UsesTable:")
        print(self.table.to_string())

    def to_log(self) -> str:
        return "UsesTable: \n" + self.table.to_string()
