from typing import List, Tuple, Set

from aitsi_parser.NextTable import NextTable
from aitsi_parser.StatementTable import StatementTable


class NextTRelation:

    def __init__(self, next_table: NextTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.next_table: NextTable = next_table
        self.stmt_table: StatementTable = stmt_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        return self.is_in_previous_line(int(param_second), int(param_first))

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[int]:
        return self.get_all_lines_in_stmt_lst_next_line(int(param_first))

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.get_all_lines_in_stmt_lst_next_line(int(param_first)))
        return self.is_in_previous_line(int(param_second), int(param_first))

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[int]:
        return self.get_all_lines_in_stmt_lst_previous_line(int(param_second))

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Tuple[List[str], List[str]]:
        return self.next_table.get_all_next(), self.next_table.get_all_previous()

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[int]:
        if param_second == '_':
            return list(map(int, self.next_table.get_all_next()))
        return self.get_all_lines_in_stmt_lst_previous_line(int(param_second))

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.get_all_lines_in_stmt_lst_previous_line(int(param_second)))
        return self.is_in_previous_line(int(param_second), int(param_first))

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[int]:
        if param_first == '_':
            return list(map(int, self.next_table.get_all_previous()))
        return self.get_all_lines_in_stmt_lst_next_line(int(param_first))

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            if param_second == '_':
                return bool(self.next_table.get_all_next() and self.next_table.get_all_previous())
            return bool(self.get_all_lines_in_stmt_lst_previous_line(int(param_second)))
        if param_second == '_':
            return bool(self.get_all_lines_in_stmt_lst_next_line(int(param_first)))
        return self.is_in_previous_line(int(param_second), int(param_first))

    def get_all_lines_in_stmt_lst_previous_line(self, line_number: int) -> List[int]:
        result: Set[int] = set()
        previous: List[int] = self.next_table.get_previous(int(line_number))
        for prev in previous:
            new_previous: Set[int] = set(self.next_table.get_previous(prev))
            if not new_previous.issubset(previous):
                previous.extend(new_previous)
            result.add(prev)
        return list(result)

    def is_in_previous_line(self, line_number: int, check_number: int) -> bool:
        previous: List[int] = self.next_table.get_previous(int(line_number))
        for prev in previous:
            if check_number in previous:
                return True
            new_previous: Set[int] = set(self.next_table.get_previous(prev))
            if not new_previous.issubset(previous):
                previous.extend(new_previous)
        return False

    def get_all_lines_in_stmt_lst_next_line(self, line_number: int) -> List[int]:
        result: Set[int] = set()
        next_lines: List[int] = self.next_table.get_next(int(line_number))
        for _next in next_lines:
            new_next: Set[int] = set(self.next_table.get_next(_next))
            if not set(new_next).issubset(next_lines):
                next_lines.extend(new_next)
            result.add(_next)
        return list(result)

    def is_in_next_line(self, line_number: int, check_number: int) -> bool:
        next_lines: List[int] = self.next_table.get_next(int(line_number))
        for _next in next_lines:
            if check_number in next_lines:
                return True
            new_next: Set[int] = set(self.next_table.get_next(_next))
            if not set(new_next).issubset(next_lines):
                next_lines.extend(new_next)
        return False
