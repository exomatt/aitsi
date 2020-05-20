from typing import List, Union

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

    def get_parent(self, stmt: int) -> Union[int, None]:
        try:
            return self.table.index[self.table[stmt] == 1].tolist()[0]
        except Exception:
            return None

    def get_child(self, stmt: int) -> List[int]:
        try:
            return self.table.columns[self.table.loc[stmt] == 1].tolist()
        except Exception:
            return []

    def is_parent(self, parent_stmt: int, child_stmt: int) -> bool:
        try:
            return bool(self.table.at[parent_stmt, child_stmt])
        except Exception:
            return False

    def to_string(self) -> None:
        print("ParentTable:")
        print(self.table.to_string())

    def to_log(self) -> str:
        return "ParentTable: \n" + self.table.to_string()
