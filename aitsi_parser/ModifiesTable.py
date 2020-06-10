from typing import List, Union, Dict


class ModifiesTable:

    def __init__(self, table: Union[Dict, List]) -> None:
        self.table: Union[Dict, List] = table

    def get_all_columns(self) -> List[str]:
        return list(self.table.keys())

    def get_all_index(self) -> List[str]:
        return list(set(sum([list(self.table[key].keys()) for key in self.table], [])))

    def get_modified(self, stmt: str) -> List[str]:
        try:
            return list(self.table[str(stmt)].keys())
        except Exception:
            return []

    def get_modifies(self, var_name: str) -> List[str]:
        try:
            return [element for element in self.table if str(var_name) in self.table[element].keys()]
        except Exception:
            return []

    def is_modified(self, stmt: str, var_name: str) -> bool:
        try:
            return bool(self.table[stmt][var_name])
        except Exception:
            return False

    def get_all_lines(self) -> List[int]:
        return [int(key) for key in self.table if str(key).isdigit()]

    def to_string(self) -> None:
        print("ModifiesTable:")
        print(self.table)

    def to_log(self) -> str:
        return "ModifiesTable: \n" + str(self.table)
