from typing import List, Union

import pandas as pd


class FollowsTable:
    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame()
        self.table: pd.DataFrame = table

    def set_follows(self, follows_stmt: int, child_stmt: int) -> None:
        if follows_stmt not in self.table.index[:]:
            indexes: List[int] = list(self.table.index[:])
            indexes.append(follows_stmt)
            self.table = self.table.reindex(indexes)
            self.table = self.table.sort_index(axis=0)
        if child_stmt not in self.table.columns.values:
            self.table[child_stmt] = pd.Series(1, index=[follows_stmt])
            self.table = self.table.sort_index(axis=1)
            self.table = self.table.fillna(value=0)
        else:
            self.table[child_stmt][follows_stmt] = 1

    def get_follows(self, stmt: int) -> Union[int, None]:
        if stmt not in self.table.columns.values:
            return None
        for i in self.table[stmt].index[:]:
            if self.table[stmt][i] == 1:
                return i
        return None

    def get_all_follows(self):
        return

    def get_child(self, stmt: int) -> Union[int, None]:
        if stmt not in self.table.index[:]:
            return None
        for col in self.table.loc[stmt].index[:]:
            if self.table.loc[stmt][col] == 1:
                return col
        return None

    def is_follows(self, follows_stmt: int, child_stmt: int) -> bool:
        if child_stmt not in self.table.columns.values or follows_stmt not in self.table.index[:]:
            return False
        return bool(self.table.at[follows_stmt, child_stmt] == 1)

    def to_string(self) -> None:
        print("followsTable:")
        print(self.table.to_string())

    def to_log(self) -> str:
        return "FollowsTable: \n" + self.table.to_string()
