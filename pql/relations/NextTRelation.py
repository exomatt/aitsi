from typing import List, Tuple, Set

from aitsi_parser.NextTable import NextTable
from aitsi_parser.StatementTable import StatementTable
from pql.Reference import Reference


class NextTRelation:

    def __init__(self, next_table: NextTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.next_table: NextTable = next_table
        self.stmt_table: StatementTable = stmt_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        return self.is_in_previous_line(int(param_second), int(param_first))

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[Reference]:
        return self.get_all_lines_in_stmt_lst_next_line(int(param_first))

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.get_all_lines_in_stmt_lst_next_line(int(param_first)))
        return self.is_in_previous_line(int(param_second), int(param_first))

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[Reference]:
        return self.get_all_lines_in_stmt_lst_previous_line(int(param_second))

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Tuple[List[Reference], List[Reference]]:
        return self.next_table.table.get_all_statements_with_next_statements(), \
               self.next_table.table.get_all_statements_with_previous_statements()

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[Reference]:
        if param_second == '_':
            return self.next_table.table.get_all_statements_with_next_statements()
        return self.get_all_lines_in_stmt_lst_previous_line(int(param_second))

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.get_all_lines_in_stmt_lst_previous_line(int(param_second)))
        return self.is_in_previous_line(int(param_second), int(param_first))

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[Reference]:
        if param_first == '_':
            return self.next_table.table.get_all_statements_with_previous_statements()
        return self.get_all_lines_in_stmt_lst_next_line(int(param_first))

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            if param_second == '_':
                return bool(self.next_table.table.index.tolist() and self.next_table.table.columns.tolist())
            return bool(self.get_all_lines_in_stmt_lst_previous_line(int(param_second)))
        if param_second == '_':
            return bool(self.get_all_lines_in_stmt_lst_next_line(int(param_first)))
        return self.is_in_previous_line(int(param_second), int(param_first))

    def get_all_lines_in_stmt_lst_previous_line(self, line_number: int) -> List[Reference]:
        result: Set[Reference] = set()
        previous: List[Reference] = self.next_table.get_previous(int(line_number))
        for prev in previous:
            new_previous: Set[Reference] = set(self.next_table.get_previous(int(prev.element)))
            if not {reference.element for reference in new_previous}.issubset(
                    {reference.element for reference in previous}):
                previous.extend(new_previous)
            result.add(prev)
        return list(result)

    def is_in_previous_line(self, line_number: int, check_number: int) -> bool:
        previous: List[Reference] = self.next_table.get_previous(int(line_number))
        for prev in previous:
            if check_number in previous:
                return True
            new_previous: Set[Reference] = set(self.next_table.get_previous(int(prev.element)))
            if not {reference.element for reference in new_previous}.issubset(
                    {reference.element for reference in previous}):
                previous.extend(new_previous)
        return False

    def get_all_lines_in_stmt_lst_next_line(self, line_number: int) -> List[Reference]:
        result: Set[Reference] = set()
        next_lines: List[Reference] = self.next_table.get_next(int(line_number))
        for _next in next_lines:
            new_next: Set[Reference] = set(self.next_table.get_next(int(_next.element)))
            if not {reference.element for reference in new_next}.issubset(
                    {reference.element for reference in next_lines}):
                next_lines.extend(new_next)
            result.add(_next)
        return list(result)

    def is_in_next_line(self, line_number: int, check_number: int) -> bool:
        next_lines: List[Reference] = self.next_table.get_next(int(line_number))
        for _next in next_lines:
            if check_number in next_lines:
                return True
            new_next: Set[Reference] = set(self.next_table.get_next(int(_next.element)))
            if not {reference.element for reference in new_next}.issubset(
                    {reference.element for reference in next_lines}):
                next_lines.extend(new_next)
        return False
