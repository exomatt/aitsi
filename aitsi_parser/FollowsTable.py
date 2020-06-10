from typing import List, Union, Dict


class FollowsTable:
    def __init__(self, table: Union[Dict, List]) -> None:
        self.table: Union[Dict, List] = table

    def get_all_columns(self) -> List[int]:
        return list(map(int, set(sum([list(self.table[key].keys()) for key in self.table], []))))

    def get_all_index(self) -> List[int]:
        return list(map(int, self.table.keys()))

    def get_follows(self, stmt: int) -> Union[int, None]:
        try:
            return int([element for element in self.table if str(stmt) in self.table[element].keys()][0])
        except Exception:
            return None

    def get_child(self, stmt: int) -> Union[int, None]:
        try:
            return int(list(self.table[str(stmt)].keys())[0])
        except Exception:
            return None

    def is_follows(self, follows_stmt: int, child_stmt: int) -> bool:
        try:
            return bool(self.table[str(follows_stmt)][str(child_stmt)])
        except Exception:
            return False

    def to_string(self) -> None:
        print("followsTable:")
        print(self.table)

    def to_log(self) -> str:
        return "FollowsTable: \n" + str(self.table)
