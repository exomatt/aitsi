from typing import List, Union, Dict


class VarTable:

    def __init__(self, table: Union[Dict, List]) -> None:
        self.table: Union[Dict, List] = table

    def get_all_var_name(self) -> List[str]:
        return [element['variable_name'] for element in self.table]

    def get_size(self) -> int:
        return len(self.table)

    def is_in(self, var_name: str) -> bool:
        for element in self.table:
            if element['variable_name'] == var_name:
                return True
        return False

    def to_string(self) -> None:
        print("VarTable:")
        print(self.table)

    def to_log(self) -> str:
        return "VarTable: \n" + str(self.table)
