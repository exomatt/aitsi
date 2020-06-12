from typing import List, Union, Dict


class CallsTable:

    def __init__(self, table: Union[Dict, List]) -> None:
        self.table: Union[Dict, List] = table

    def get_all_columns(self) -> List[str]:
        return sum([list(self.table[key].keys()) for key in self.table], [])

    def get_all_index(self) -> List[str]:
        return list(self.table.keys())

    def get_calls(self, procedure: str) -> List[str]:
        try:
            return [element for element in self.table if procedure in self.table[element].keys()]
        except Exception:
            return []

    def get_called_from(self, procedure: str) -> List[str]:
        try:
            return list(self.table[procedure].keys())
        except Exception:
            return []

    def is_calls(self, call_procedure: str, receiving_procedure: str) -> bool:
        try:
            return bool(self.table[call_procedure][receiving_procedure])
        except Exception:
            return False

    def to_string(self) -> None:
        print("CallsTable:")
        print(self.table)

    def to_log(self) -> str:
        return "CallsTable: \n" + str(self.table)
