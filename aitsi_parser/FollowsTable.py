from typing import List, Union

import pandas as pd


class FollowsTable:
    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame()
        self.table: pd.DataFrame = table

    def set_follows(self, follows_stmt: int, child_stmt: int) -> None:
        if child_stmt not in self.table.columns.tolist():
            self.table[child_stmt] = 0
        if follows_stmt not in self.table.index.tolist():
            self.table.loc[follows_stmt] = 0
        self.table.loc[follows_stmt, child_stmt] = 1

    def get_follows(self, stmt: int) -> Union[int, None]:
        try:
            return self.table.index[self.table[stmt] == 1].tolist()[0]
        except Exception:
            return None

    def get_child(self, stmt: int) -> Union[int, None]:
        try:
            return self.table.columns[self.table.loc[stmt] == 1].tolist()[0]
        except Exception:
            return None

    def is_follows(self, follows_stmt: int, child_stmt: int) -> bool:
        try:
            return bool(self.table.at[follows_stmt, child_stmt])
        except Exception:
            return False

    def to_string(self) -> None:
        print("followsTable:")
        print(self.table.to_string())

    def to_log(self) -> str:
        return "FollowsTable: \n" + self.table.to_string()
