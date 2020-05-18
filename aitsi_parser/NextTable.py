from typing import List

import numpy as np
import pandas as pd


class NextTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame()
        self.table: pd.DataFrame = table

    def set_next(self, previous_stmt: int, next_stmt: int) -> None:
        if previous_stmt not in self.table.index[:]:
            indexes: List[int] = list(self.table.index[:])
            indexes.append(previous_stmt)
            self.table = self.table.reindex(indexes)
            self.table = self.table.sort_index(axis=0)
        if next_stmt not in self.table.columns.values:
            self.table[next_stmt] = pd.Series(1, index=[previous_stmt])
            self.table = self.table.sort_index(axis=1)
            self.table = self.table.fillna(value=0)
        else:
            self.table[next_stmt][previous_stmt] = 1

    def remove_next(self, stmt: int) -> None:
        self.table = self.table.drop([stmt])
        self.table = self.table.replace(0, np.nan).dropna(axis=1, how='all').fillna(0)

    def get_previous(self, stmt: int) -> List[int]:
        try:
            return self.table.index[self.table[stmt] == 1].tolist()
        except Exception:
            return []

    def get_next(self, stmt: int) -> List[int]:
        try:
            return self.table.columns[self.table.loc[stmt] == 1].tolist()
        except Exception:
            return []

    def is_next(self, previous_stmt: int, next_stmt: int) -> bool:
        try:
            return bool(self.table.at[previous_stmt, next_stmt])
        except Exception:
            return False

    def to_string(self) -> None:
        print("NextTable:")
        print(self.table.to_string())

    def to_log(self) -> str:
        return "NextTable: \n" + self.table.to_string()
