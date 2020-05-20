from typing import List, Union, Tuple, Set

from aitsi_parser.NextTable import NextTable
from aitsi_parser.StatementTable import StatementTable


class NextTRelation:
    statements = ['WHILE', 'IF', 'CALL', 'ASSIGN']

    def __init__(self, next_table: NextTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.next_table: NextTable = next_table
        self.stmt_table: StatementTable = stmt_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        pass

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[str]:
        pass

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        pass

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[str]:
        pass

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Tuple[List[str], List[str]]:
        pass

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[str]:
        pass

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        pass

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[str]:
        pass

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        pass

    def execute(self, param_first: str, param_second: str) -> Union[Tuple[bool, None],
                                                                    Tuple[List[int], None],
                                                                    Tuple[List[int], List[int]]]:
        if param_first.isdigit():
            if param_second.isdigit():
                # p1 i p2 sa liczbami
                return self._next_T_two_digit(param_first, param_second)
            elif param_second == '_':
                # p1 jest liczba, a p2  "_"
                return self._next_T_digit_wildcard(param_first)
            else:
                # p1 jest liczba, a p2 str np. "CALL"
                return self._next_T_digit_stmt(param_first, param_second)
        elif param_first == '_':
            if param_second.isdigit():
                return self._next_T_wildcard_digit(param_second)
            elif param_second == '_':
                # p1  "_", a p2  "_"
                raise Exception("Imposible Next*(_,_) albo klasyk dupa 1 i dupa 2 sie nie moga wydarzyć XD  ")
            else:
                # p1  "_", a p2 str np. "CALL"
                return self._next_T_wildcard_stmt(param_second)
        else:
            if param_second.isdigit():
                # p1 str np. "IF"  p2 jest liczba
                return self._next_T_stmt_digit(param_first, param_second)

            elif param_second == '_':
                # p1 str np. "IF", a p2  "_"
                return self._next_T_stmt_wildcard(param_first)
            else:
                # p1 str np. "IF", a p2 str np. "CALL"
                return self._next_T_two_str_types(param_first, param_second)

    def _next_T_stmt_wildcard(self, param_first) -> Tuple[List[int], None]:
        result: Set[int] = set()
        previous: List[int] = []
        lines_by_type_name: List[int] = []
        for stmt in self.statements:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        for line in lines_by_type_name:
            previous.extend(self.next_table.get_previous(line))
        if param_first == 'STMT':
            for prev in previous:
                new_previous: Set[int] = set(self.next_table.get_previous(prev))
                if not set(new_previous).issubset(previous):
                    previous.extend(new_previous)
                if self.stmt_table.get_other_info(prev)['name'] in self.statements:
                    result.add(prev)
        else:
            for prev in previous:
                new_previous: Set[int] = set(self.next_table.get_previous(prev))
                if not set(new_previous).issubset(previous):
                    previous.extend(new_previous)
                if self.stmt_table.get_other_info(prev)['name'] == param_first:
                    result.add(prev)
        return list(result), None

    def _next_T_stmt_digit(self, param_first, param_second) -> Tuple[List[int], None]:
        result: Set[int] = set()
        previous: List[int] = self.next_table.get_previous(int(param_second))
        new_previous: Set[int] = set()
        if param_first == 'STMT':
            for prev in previous:
                new_previous = set(self.next_table.get_previous(prev))
                if not set(new_previous).issubset(previous):
                    previous.extend(new_previous)
                if self.stmt_table.get_other_info(prev)['name'] in self.statements:
                    result.add(prev)
        else:
            for prev in previous:
                new_previous = set(self.next_table.get_previous(prev))
                if not set(new_previous).issubset(previous):
                    previous.extend(new_previous)
                if self.stmt_table.get_other_info(prev)['name'] == param_first:
                    result.add(prev)
        return list(result), None

    def _next_T_wildcard_stmt(self, param_second) -> Tuple[List[int], None]:
        result: Set[int] = set()
        previous: List[int] = []
        lines_by_type_name: List[int] = []
        if param_second == 'STMT':
            for stmt in self.statements:
                lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_second))
        for line in lines_by_type_name:
            previous.extend(self.next_table.get_previous(line))
        for prev in previous:
            new_previous: Set[int] = set(self.next_table.get_previous(prev))
            if not set(new_previous).issubset(previous):
                previous.extend(new_previous)
            if self.stmt_table.get_other_info(prev)['name'] in self.statements:
                result.add(prev)
        return list(result), None

    def _next_T_wildcard_digit(self, param_second) -> Tuple[List[int], None]:
        previous: List[int] = self.next_table.get_previous(int(param_second))
        for prev in previous:
            new_previous: Set[int] = set(self.next_table.get_previous(prev))
            if not set(new_previous).issubset(previous):
                previous.extend(new_previous)
        return list(previous), None

    def _next_T_digit_stmt(self, param_first, param_second) -> Tuple[List[int], None]:
        result: Set[int] = set()
        next_lines: List[int] = self.next_table.get_next(int(param_first))
        if param_second == 'STMT':
            for _next in next_lines:
                new_next: Set[int] = set(self.next_table.get_next(_next))
                if not set(new_next).issubset(next_lines):
                    next_lines.extend(new_next)
                if self.stmt_table.get_other_info(_next)['name'] in self.statements:
                    result.add(_next)
            return list(result), None
        else:
            for _next in next_lines:
                new_next: Set[int] = set(self.next_table.get_next(_next))
                if not set(new_next).issubset(next_lines):
                    next_lines.extend(new_next)
                if self.stmt_table.get_other_info(_next)['name'] in param_second:
                    result.add(_next)
            return list(result), None

    def _next_T_digit_wildcard(self, param_first) -> Tuple[List[int], None]:
        next_lines: List[int] = self.next_table.get_next(int(param_first))
        for _next in next_lines:
            new_next: Set[int] = set(self.next_table.get_next(_next))
            if not set(new_next).issubset(next_lines):
                next_lines.extend(new_next)
        return list(next_lines), None

    def _next_T_two_digit(self, param_first, param_second) -> Tuple[bool, None]:
        is_next = self.next_table.is_next(int(param_first), int(param_second))
        if is_next:
            return is_next, None
        else:
            next_values: List[int] = self.next_table.get_next(int(param_first))
            for _next in next_values:
                if int(param_second) in self.next_table.get_next(_next):
                    return True, None
                new_next: Set[int] = set(self.next_table.get_next(_next))
                if not set(new_next).issubset(next_values):
                    next_values.extend(new_next)
            return False, None

    def _next_T_two_str_types(self, param_first, param_second) -> Tuple[List[int], List[int]]:
        result_left = self._result_left_next_T_two_str(param_first, param_second)
        result_right = self._result_right_next_T_two_str(param_first, param_second)
        return list(result_left), list(result_right)

    def _result_left_next_T_two_str(self, param_first, param_second) -> Set[int]:
        result_left: Set[int] = set()
        previous: List[int] = []
        lines_by_type_name: List[int] = []
        if param_second == 'STMT':
            for stmt in self.statements:
                lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_second))
        for line in lines_by_type_name:
            previous.extend(self.next_table.get_previous(line))
        if param_first == 'STMT':
            for prev in previous:
                new_previous: Set[int] = set(self.next_table.get_previous(prev))
                if not set(new_previous).issubset(previous):
                    previous.extend(new_previous)
                if self.stmt_table.get_other_info(prev)['name'] in self.statements:
                    result_left.add(prev)
        else:
            for prev in previous:
                new_previous: Set[int] = set(self.next_table.get_previous(prev))
                if not set(new_previous).issubset(previous):
                    previous.extend(new_previous)
                if self.stmt_table.get_other_info(prev)['name'] == param_first:
                    result_left.add(prev)
        return result_left

    def _result_right_next_T_two_str(self, param_first, param_second) -> Set[int]:
        result_right: Set[int] = set()
        next_lines: List[int] = []
        lines_by_type_name: List[int] = []
        if param_first == 'STMT':
            for stmt in self.statements:
                lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_first))
        for line in lines_by_type_name:
            next_lines.extend(self.next_table.get_next(line))
        if param_second == 'STMT':
            for _next in next_lines:
                new_next: Set[int] = set(self.next_table.get_next(_next))
                if not set(new_next).issubset(next_lines):
                    next_lines.extend(new_next)
                if self.stmt_table.get_other_info(_next)['name'] in self.statements:
                    result_right.add(_next)
        else:
            for _next in next_lines:
                new_next: Set[int] = set(self.next_table.get_next(_next))
                if not set(new_next).issubset(next_lines):
                    next_lines.extend(new_next)
                if self.stmt_table.get_other_info(_next)['name'] == param_second:
                    result_right.add(_next)
        return result_right
