from typing import List, Union, Dict


class ParentTable:

    def __init__(self, table: Union[Dict, List]) -> None:
        self.table: Union[Dict, List] = table

    def get_all_parents(self) -> List[int]:
        return list(map(int, list(self.table.keys())))

    def get_all_children(self) -> List[int]:
        return list(map(int, set(sum([list(self.table[key].keys()) for key in self.table], []))))

    def get_parent(self, stmt: int) -> Union[int, None]:
        try:
            return [int(element) for element in self.table if str(stmt) in self.table[element].keys()][0]
        except Exception:
            return None

    def get_child(self, stmt: int) -> List[int]:
        try:
            return list(map(int, list(self.table[str(stmt)].keys())))
        except Exception:
            return []

    def is_parent(self, parent_stmt: int, child_stmt: int) -> bool:
        try:
            return bool(self.table[str(parent_stmt)][str(child_stmt)])
        except Exception:
            return False

    def to_string(self) -> None:
        print("ParentTable:")
        print(self.table)

    def to_log(self) -> str:
        return "ParentTable: \n" + str(self.table)
