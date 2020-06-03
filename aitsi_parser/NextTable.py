from typing import List

import numpy as np
import pandas as pd

from pql.Reference import Reference


class NextTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame()
        self.table: pd.DataFrame = table

    def set_next(self, previous_stmt: int, next_stmt: int) -> None:
        if next_stmt not in self.table.columns.tolist():
            self.table[next_stmt] = 0
        if previous_stmt not in self.table.index.tolist():
            self.table.loc[previous_stmt] = 0
        self.table.loc[previous_stmt, next_stmt] = 1

    def remove_next(self, stmt: int) -> None:
        self.table = self.table.drop([stmt])
        self.table = self.table.replace(0, np.nan).dropna(axis=1, how='all').fillna(0)

    def get_all_statements_with_next_statements(self):
        return sum([self.get_next(stmt) for stmt in self.table.index.tolist()], [])

    def get_all_statements_with_previous_statements(self):
        return sum([self.get_previous(stmt) for stmt in self.table.columns.tolist()], [])

    def get_previous(self, stmt: int) -> List[Reference]:
        try:
            return [Reference(index, stmt) for index in self.table.index[self.table[stmt] == 1].tolist()]
        except Exception:
            return []

    def get_next(self, stmt: int) -> List[Reference]:
        try:
            return [Reference(column, stmt) for column in self.table.columns[self.table.loc[stmt] == 1].tolist()]
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
