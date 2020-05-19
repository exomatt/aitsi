from typing import List

import pandas as pd


class CallsTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame()
        self.table: pd.DataFrame = table

    def set_calls(self, call_procedure: str, receiving_procedure: str) -> None:
        if call_procedure not in self.table.index[:]:
            indexes: List[str] = list(self.table.index[:])
            indexes.append(call_procedure)
            self.table = self.table.reindex(indexes)
            self.table = self.table.sort_index(axis=0)

        if receiving_procedure not in self.table.columns.values:
            self.table[receiving_procedure] = pd.Series(1, index=[call_procedure])
            self.table = self.table.sort_index(axis=1)
            self.table = self.table.fillna(value=0)
        else:
            self.table[receiving_procedure][call_procedure] = 1
            self.table = self.table.fillna(value=0)

    def get_calls(self, procedure: str) -> List[str]:
        try:
            return self.table.index[self.table[procedure] == 1].tolist()
        except Exception:
            return []

    def get_called_from(self, procedure: str) -> List[str]:
        try:
            return self.table.columns[self.table.loc[procedure] == 1].tolist()
        except Exception:
            return []

    def is_calls(self, call_procedure: str, receiving_procedure: str) -> bool:
        try:
            return bool(self.table.at[call_procedure, receiving_procedure])
        except Exception:
            return False

    def to_string(self) -> None:
        print("CallsTable:")
        print(self.table.to_string())

    def to_log(self) -> str:
        return "CallsTable: \n" + self.table.to_string()
