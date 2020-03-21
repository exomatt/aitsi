from typing import List

import pandas as pd


class ParentTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame()
        self.table: pd.DataFrame = table

    def set_parent(self, parent_stmt: int, child_stmt: int) -> None:
        if parent_stmt not in self.table.index[:]:
            indexes: List[int] = list(self.table.index[:])
            indexes.append(parent_stmt)
            self.table = self.table.reindex(indexes)
            self.table = self.table.sort_index(axis=0)
        if child_stmt not in self.table.columns.values:
            self.table[child_stmt] = pd.Series(1, index=[parent_stmt])
            self.table = self.table.sort_index(axis=1)
            self.table = self.table.fillna(value=0)
        else:
            self.table[child_stmt][parent_stmt] = 1

    def get_parent(self, stmt: int) -> List[int]:
        results: List[int] = []
        if stmt not in self.table.columns.values:
            return results
        for i in self.table[stmt].index[:]:
            if self.table[stmt][i] == 1:
                results.append(i)
        return results

    def get_child(self, stmt: int) -> List[int]:
        results: List[int] = []
        if stmt not in self.table.index[:]:
            return results
        for col in self.table.loc[stmt].index[:]:
            if self.table.loc[stmt][col] == 1:
                results.append(col)
        return results

    def is_parent(self, parent_stmt: int, child_stmt: int) -> bool:
        if child_stmt not in self.table.columns.values or parent_stmt not in self.table.index[:]:
            return False
        return self.table.at[parent_stmt, child_stmt] == 1

    def to_string(self) -> None:
        print("ParentTable:")
        print(self.table.to_string())
