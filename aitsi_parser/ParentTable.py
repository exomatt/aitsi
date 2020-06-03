from typing import List, Union

import pandas as pd

from pql.Reference import Reference


class ParentTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame()
        self.table: pd.DataFrame = table

    def set_parent(self, parent_stmt: int, child_stmt: int) -> None:
        if child_stmt not in self.table.columns.tolist():
            self.table[child_stmt] = 0
        if parent_stmt not in self.table.index.tolist():
            self.table.loc[parent_stmt] = 0
        self.table.loc[parent_stmt, child_stmt] = 1

    def get_all_children(self) -> List[Reference]:
        return sum([self.get_child(follows) for follows in self.table.index.tolist()], [])

    def get_all_parents(self) -> List[Reference]:
        return list(
            filter(lambda reference: reference, [self.get_parent(child) for child in self.table.columns.tolist()]))

    def get_parent(self, stmt: int) -> Union[Reference, None]:
        try:
            return Reference(self.table.index[self.table[stmt] == 1].tolist()[0], str(stmt))
        except Exception:
            return None

    def get_child(self, stmt: int) -> List[Reference]:
        try:
            return [Reference(line, str(stmt)) for line in self.table.columns[self.table.loc[stmt] == 1].tolist()]
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
