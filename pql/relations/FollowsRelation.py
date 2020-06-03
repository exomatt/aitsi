from typing import List, Union, Tuple

from aitsi_parser import FollowsTable
from aitsi_parser.StatementTable import StatementTable
from pql.Reference import Reference


class FollowsRelation:
    statements = ['WHILE', 'IF', 'CALL', 'ASSIGN']

    def __init__(self, follows_table: FollowsTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.stmt_table: StatementTable = stmt_table
        self.follows_table: FollowsTable = follows_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        return self.follows_table.is_follows(int(param_first), int(param_second))

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[Reference]:
        child: Union[Reference, None] = self.follows_table.get_child(int(param_first))
        if child:
            if param_second == 'STMT' or int(child.element) in self.stmt_table.get_statement_line_by_type_name(
                    param_second):
                return [child]
            else:
                return []
        else:
            return []

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.follows_table.get_child(int(param_first)))
        return self.follows_table.is_follows(int(param_first), int(param_second))

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[Reference]:
        follows_line: Union[Reference, None] = self.follows_table.get_follows(int(param_second))
        if follows_line is not None:
            if param_first == 'STMT' or int(follows_line.element) in self.stmt_table.get_statement_line_by_type_name(
                    param_first):
                return [follows_line]
            else:
                return []
        else:
            return []

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Tuple[List[Reference], List[Reference]]:
        if param_first == 'STMT':
            if param_second == 'STMT':
                return self.follows_table.get_all_follows(), \
                       self.follows_table.get_all_children()
            param_first_reference: List[Reference] = self.follows_table.get_all_follows()
            param_second_lines: List[int] = list(
                set(self.stmt_table.get_statement_line_by_type_name(param_second)).intersection(
                    set(self.follows_table.table.columns.tolist())))
            param_second_reference: List[Reference] = []
            for reference in param_first_reference:
                if int(reference.reference) in param_second_lines:
                    param_second_reference.append(Reference(reference.reference, reference.element))
            return param_first_reference, param_second_reference
        else:
            param_first_lines: List[Reference] = list(
                filter(lambda line: line, [self.follows_table.get_child(int(line)) for line in list(
                    set(self.stmt_table.get_statement_line_by_type_name(param_first)).intersection(
                        set(self.follows_table.table.index.tolist())))]))
            if param_second == 'STMT':
                return param_first_lines, list(filter(lambda line: line,
                                                      [self.follows_table.get_child(int(line.element)) for line in
                                                       param_first_lines]))
            else:
                second_lines: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
                first_result: List[Reference] = []
                param_second_lines: List[Reference] = []
                for reference in param_first_lines:
                    if int(reference.element) in second_lines:
                        first_result.append(reference)
                        param_second_lines.append(Reference(reference.reference, reference.element))
                return first_result, param_second_lines

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[Reference]:
        if param_second == '_':
            if param_first == 'STMT':
                return self.follows_table.get_all_follows()
            else:
                return [Reference(reference.reference, reference.element) for reference in list(
                    filter(lambda line: line is not None, [self.follows_table.get_child(int(line)) for line in
                                                           self.stmt_table.get_statement_line_by_type_name(
                                                               param_first)]))]
        return self.not_initialized_set_and_value_from_set(param_first, param_second)

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.follows_table.get_child(int(param_second)))
        return bool(self.follows_table.is_follows(int(param_first), int(param_second)))

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[Reference]:
        if param_first == '_':
            if param_second == 'STMT':
                return self.follows_table.get_all_follows()
            return list(filter(lambda line: line is not None, [self.follows_table.get_child(int(line)) for line in
                                                               self.stmt_table.get_statement_line_by_type_name(
                                                                   param_second)]))
        return self.value_from_set_and_not_initialized_set(param_first, param_second)

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            if param_second == '_':
                return bool(self.follows_table.table.index.tolist() and self.follows_table.table.columns.tolist())
            return bool(self.follows_table.get_child(int(param_second)))
        if param_second == '_':
            return bool(self.follows_table.get_child(int(param_first)))
        return bool(self.follows_table.is_follows(int(param_first), int(param_second)))
