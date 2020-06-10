from typing import List, Union, Dict


class ConstTable:

    def __init__(self, table: Union[Dict, List]) -> None:
        self.table: Union[Dict, List] = table

    def get_all_constant(self) -> List[str]:
        return list(map(int, list(self.table.keys())))

    def get_other_info(self, constant: int) -> dict:
        return self.table[constant]

    def get_size(self) -> int:
        return len(self.table)

    def is_in(self, constant: int) -> bool:
        return constant in self.table.keys()

    def to_string(self) -> None:
        print("ConstTable:")
        print(self.table)

    def to_log(self) -> str:
        return "ConstTable: \n" + str(self.table)
