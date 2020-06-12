from typing import List, Tuple

from aitsi_parser.NextTable import NextTable
from aitsi_parser.StatementTable import StatementTable


class NextRelation:

    def __init__(self, next_table: NextTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.next_table: NextTable = next_table
        self.stmt_table: StatementTable = stmt_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        return self.next_table.is_next(int(param_first), int(param_second))

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[int]:
        return self.next_table.get_next(int(param_first))

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.next_table.get_next(int(param_first)))
        return self.next_table.is_next(int(param_first), int(param_second))

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[int]:
        return self.next_table.get_previous(int(param_second))

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Tuple[List[str], List[str]]:
        return self.next_table.get_all_next(), self.next_table.get_all_previous()

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[int]:
        if param_second == '_':
            return list(map(int, self.next_table.get_all_next()))
        return self.next_table.get_previous(int(param_second))

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.next_table.get_previous(int(param_second)))
        return self.next_table.is_next(int(param_first), int(param_second))

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[int]:
        if param_first == '_':
            return list(map(int, self.next_table.get_all_previous()))
        return self.next_table.get_next(int(param_first))

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            if param_second == '_':
                return bool(self.next_table.get_all_next() and self.next_table.get_all_previous())
            return bool(self.next_table.get_previous(int(param_second)))
        if param_second == '_':
            return bool(self.next_table.get_next(int(param_first)))
        return self.next_table.is_next(int(param_first), int(param_second))
