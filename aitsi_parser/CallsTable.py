from typing import List

import pandas as pd

from pql.Reference import Reference


class CallsTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame()
        self.table: pd.DataFrame = table

    def set_calls(self, call_procedure: str, receiving_procedure: str) -> None:
        if receiving_procedure not in self.table.columns.tolist():
            self.table[receiving_procedure] = 0
        if call_procedure not in self.table.index.tolist():
            self.table.loc[call_procedure] = 0
        self.table.loc[call_procedure, receiving_procedure] = 1

    def get_all_procedures_with_procedures_they_are_called_from(self):
        return sum([self.get_called_from(procedure) for procedure in self.table.index.tolist()], [])

    def get_all_procedures_with_procedures_they_calls(self):
        return sum([self.get_calls(procedure) for procedure in self.table.columns.tolist()], [])

    def get_calls(self, procedure: str) -> List[Reference]:
        try:
            return [Reference(index, procedure) for index in self.table.index[self.table[procedure] == 1].tolist()]
        except Exception:
            return []

    def get_called_from(self, procedure: str) -> List[Reference]:
        try:
            return [Reference(column, procedure) for column in
                    self.table.columns[self.table.loc[procedure] == 1].tolist()]
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
