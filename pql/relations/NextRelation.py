from typing import List, Union, Tuple, Set

from aitsi_parser.NextTable import NextTable
from aitsi_parser.StatementTable import StatementTable


class NextRelation:
    statements = ['WHILE', 'IF', 'CALL', 'ASSIGN']

    def __init__(self, next_table: NextTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.next_table: NextTable = next_table
        self.stmt_table: StatementTable = stmt_table

    def execute(self, param_first: str, param_second: str) -> Union[Tuple[bool, None],
                                                                    Tuple[List[int], None],
                                                                    Tuple[list, list]]:
        if param_first.isdigit():
            if param_second.isdigit():
                # p1 i p2 sa liczbami
                return self.next_table.is_next(int(param_first), int(param_second)), None
            elif param_second == '_':
                # p1 jest liczba, a p2  "_" Next(2,_)
                return self.next_table.get_next(int(param_first)), None
            else:
                # p1 jest liczba, a p2 str np. "CALL"
                return self._next_digit_stmt(param_first, param_second)
        elif param_first == '_':
            if param_second.isdigit():
                # p1  "_"  p2 jest liczba
                return self.next_table.get_previous(int(param_second)), None
            elif param_second == '_':
                # p1  "_", a p2  "_"
                raise Exception("Imposible Next(_,_) albo klasyk dupa 1 i dupa 2 sie nie moga wydarzyć XD  ")
            else:
                # p1  "_", a p2 str np. "CALL"
                return self._next_wildcard_stmt(param_second)
        else:
            if param_second.isdigit():
                # p1 str np. "IF"  p2 jest liczba
                return self._next_stmt_liczba(param_first, param_second)
            elif param_second == '_':
                # p1 str np. "IF", a p2  "_"
                return self._str_stmt_wildcard(param_first)
            else:
                # p1 str np. "IF", a p2 str np. "CALL"
                result_left = self._get_left_result_two_str_types(param_first, param_second)
                result_right = self._get_right_result_two_str_types(param_first, param_second)
                return list(result_left), list(result_right)

    def _str_stmt_wildcard(self, param_first) -> Tuple[List[int], None]:
        result: Set[int] = set()
        previous: List[int] = []
        lines_by_type_name: List[int] = []
        for stmt in self.statements:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        for line in lines_by_type_name:
            new_previous: Set[int] = set(self.next_table.get_previous(line))
            if not set(new_previous).issubset(previous):
                previous.extend(new_previous)

        if param_first == 'STMT':
            for prev in previous:
                if self.stmt_table.get_other_info(prev)['name'] in self.statements:
                    result.add(prev)
        else:
            for prev in previous:
                if self.stmt_table.get_other_info(prev)['name'] == param_first:
                    result.add(prev)
        return list(result), None

    def _next_stmt_liczba(self, param_first, param_second) -> Tuple[List[int], None]:
        result: Set[int] = set()
        previous = self.next_table.get_previous(int(param_second))
        if param_first == 'STMT':
            for prev in previous:
                if self.stmt_table.get_other_info(prev)['name'] in self.statements:
                    result.add(prev)
        else:
            for prev in previous:
                if self.stmt_table.get_other_info(prev)['name'] == param_first:
                    result.add(prev)
        return list(result), None

    def _next_wildcard_stmt(self, param_second) -> Tuple[List[int], None]:
        result: Set[int] = set()
        previous: List[int] = []
        lines_by_type_name: List[int] = []
        if param_second == 'STMT':
            for stmt in self.statements:
                lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_second))
        for line in lines_by_type_name:
            new_previous: Set[int] = set(self.next_table.get_previous(line))
            if not set(new_previous).issubset(previous):
                previous.extend(new_previous)
        for prev in previous:
            if self.stmt_table.get_other_info(prev)['name'] in self.statements:
                result.add(prev)
        return list(result), None

    def _next_digit_stmt(self, param_first, param_second) -> Tuple[List[int], None]:
        result: Set[int] = set()
        next_lines: List[int] = self.next_table.get_next(int(param_first))
        if param_second == 'STMT':
            for line in next_lines:
                if self.stmt_table.get_other_info(line)['name'] in self.statements:
                    result.add(line)
            return list(result), None
        else:
            for line in next_lines:
                if self.stmt_table.get_other_info(line)['name'] in param_second:
                    result.add(line)
            return list(result), None

    def _get_right_result_two_str_types(self, param_first, param_second):
        result_right: Set[int] = set()
        next_lines: List[int] = []
        lines_by_type_name_right: List[int] = []
        if param_first == 'STMT':
            for stmt in self.statements:
                lines_by_type_name_right.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_by_type_name_right.extend(self.stmt_table.get_statement_line_by_type_name(param_first))
        for line in lines_by_type_name_right:
            new_next: Set[int] = set(self.next_table.get_next(line))
            if not set(new_next).issubset(next_lines):
                next_lines.extend(new_next)
        if param_second == 'STMT':
            for _next in next_lines:
                if self.stmt_table.get_other_info(_next)['name'] in self.statements:
                    result_right.add(_next)
        else:
            for _next in next_lines:
                if self.stmt_table.get_other_info(_next)['name'] == param_second:
                    result_right.add(_next)
        return result_right

    def _get_left_result_two_str_types(self, param_first, param_second):
        result_left: Set[int] = set()
        previous: List[int] = []
        lines_by_type_name_left: List[int] = []
        if param_second == 'STMT':
            for stmt in self.statements:
                lines_by_type_name_left.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_by_type_name_left.extend(self.stmt_table.get_statement_line_by_type_name(param_second))
        for line in lines_by_type_name_left:
            new_previous: Set[int] = set(self.next_table.get_previous(line))
            if not set(new_previous).issubset(previous):
                previous.extend(new_previous)
        if param_first == 'STMT':
            for prev in previous:
                if self.stmt_table.get_other_info(prev)['name'] in self.statements:
                    result_left.add(prev)
        else:
            for prev in previous:
                if self.stmt_table.get_other_info(prev)['name'] == param_first:
                    result_left.add(prev)
        return result_left
