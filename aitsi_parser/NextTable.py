from typing import List, Union, Dict


class NextTable:

    def __init__(self, table: Union[Dict, List]) -> None:
        self.table: Union[Dict, List] = table

    def get_all_previous(self) -> List[int]:
        return list(map(int, list(self.table.keys())))

    def get_all_next(self) -> List[int]:
        return list(map(int, set(sum([list(self.table[key].keys()) for key in self.table], []))))

    def get_previous(self, stmt: int) -> List[int]:
        try:
            return list(map(int, list(self.table[str(stmt)].keys())))
        except Exception:
            return []

    def get_next(self, stmt: int) -> List[int]:
        try:
            return [int(element) for element in self.table if str(stmt) in self.table[element].keys()]
        except Exception:
            return []

    def is_next(self, previous_stmt: int, next_stmt: int) -> bool:
        try:
            return bool(self.table[str(next_stmt)][str(previous_stmt)])
        except Exception:
            return False

    def to_string(self) -> None:
        print("NextTable:")
        print(self.table)

    def to_log(self) -> str:
        return "NextTable: \n" + str(self.table)
