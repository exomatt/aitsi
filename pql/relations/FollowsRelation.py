from typing import List, Union, Tuple

from aitsi_parser import FollowsTable
from aitsi_parser.StatementTable import StatementTable


class FollowsRelation:
    statements = ['WHILE', 'IF', 'CALL', 'ASSIGN']

    def __init__(self, follows_table: FollowsTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.stmt_table: StatementTable = stmt_table
        self.follows_table: FollowsTable = follows_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        return self.follows_table.is_follows(int(param_first), int(param_second))

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[int]:
        child_line: Union[int, None] = self.follows_table.get_child(int(param_first))
        if child_line is not None:
            if param_second == 'STMT' or child_line in self.stmt_table.get_statement_line_by_type_name(param_second):
                return [child_line]
            else:
                return []
        else:
            return []

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.follows_table.get_child(int(param_first)))
        return self.follows_table.is_follows(int(param_first), int(param_second))

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[int]:
        follows_line: Union[int, None] = self.follows_table.get_follows(int(param_second))
        if follows_line is not None:
            if param_first == 'STMT' or follows_line in self.stmt_table.get_statement_line_by_type_name(param_first):
                return [follows_line]
            else:
                return []
        else:
            return []

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Tuple[List[int], List[int]]:
        if param_first == 'STMT':
            if param_second == 'STMT':
                return self.follows_table.table.index.tolist(), self.follows_table.table.columns.tolist()
            else:
                param_second_lines: List[int] = list(
                    set(self.stmt_table.get_statement_line_by_type_name(param_second)).intersection(
                        set(self.follows_table.table.columns.tolist())))
                return list(filter(lambda line: line is not None, [self.follows_table.get_follows(line) for line in
                                                                   param_second_lines])), param_second_lines
        else:
            param_first_lines: List[int] = list(
                set(self.stmt_table.get_statement_line_by_type_name(param_first)).intersection(
                    set(self.follows_table.table.index.tolist())))
            if param_second == 'STMT':
                return param_first_lines, list(filter(lambda line: line is not None,
                                                      [self.follows_table.get_child(line) for line in
                                                       param_first_lines]))
            else:
                param_second_lines: List[int] = list(
                    set(self.stmt_table.get_statement_line_by_type_name(param_second)).intersection(
                        set(self.follows_table.table.columns.tolist())))
                return list(filter(lambda line: line is not None, [line for line in param_first_lines if
                                                                   self.follows_table.get_child(
                                                                       line) in param_second_lines])), \
                       list(filter(lambda line: line is not None, [line for line in param_second_lines if
                                                                   self.follows_table.get_follows(
                                                                       line) in param_first_lines]))

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[int]:
        if param_second == '_':
            if param_first == 'STMT':
                return self.follows_table.table.index.tolist()
            else:
                return list(set(self.stmt_table.get_statement_line_by_type_name(param_first)).intersection(
                    set(self.follows_table.table.index.tolist())))
        return self.not_initialized_set_and_value_from_set(param_first, param_second)

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.follows_table.get_child(int(param_second)))
        return bool(self.follows_table.is_follows(int(param_first), int(param_second)))

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[int]:
        if param_first == '_':
            if param_second == 'STMT':
                return self.follows_table.table.columns.tolist()
            else:
                lines_numbers: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
                return [line for line in lines_numbers if self.follows_table.get_follows(line) is not None]
        return self.value_from_set_and_not_initialized_set(param_first, param_second)

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            if param_second == '_':
                return bool(self.follows_table.table.index.tolist() and self.follows_table.table.columns.tolist())
            return bool(self.follows_table.get_child(int(param_second)))
        if param_second == '_':
            return bool(self.follows_table.get_child(int(param_first)))
        return bool(self.follows_table.is_follows(int(param_first), int(param_second)))
