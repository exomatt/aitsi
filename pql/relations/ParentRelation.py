from typing import List, Tuple, Union

from aitsi_parser.ParentTable import ParentTable
from aitsi_parser.StatementTable import StatementTable
from pql.Reference import Reference


class ParentRelation:

    def __init__(self, parent_table: ParentTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.parent_table: ParentTable = parent_table
        self.stmt_table: StatementTable = stmt_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        return self.parent_table.is_parent(int(param_first), int(param_second))

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[Reference]:
        if param_second == 'STMT':
            return self.parent_table.get_child(int(param_first))
        param_second_lines: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
        return list(filter(lambda reference: int(reference.element) in param_second_lines,
                           self.parent_table.get_child(int(param_first))))

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.parent_table.get_child(int(param_first)))
        return self.parent_table.is_parent(int(param_first), int(param_second))

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[Reference]:
        parent: Union[Reference, None] = self.parent_table.get_parent(int(param_second))
        if parent is not None:
            if param_first == 'STMT' or int(parent.element) in self.stmt_table.get_statement_line_by_type_name(
                    param_first):
                return [parent]
            else:
                return []
        else:
            return []

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Tuple[List[Reference], List[Reference]]:
        if param_first == 'STMT':
            if param_second == 'STMT':
                return self.parent_table.get_all_parents(), \
                       self.parent_table.get_all_children()
            param_second_lines: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
            param_first_reference: List[Reference] = list(filter(lambda reference: reference,
                                                                 sum([self.parent_table.get_child(line) for line in
                                                                      self.stmt_table.get_all_statement_lines()], [])))
            param_second_reference: List[Reference] = list(filter(lambda reference: reference,
                                                                  [self.parent_table.get_parent(line) for line in
                                                                   param_second_lines]))
            return [reference.reverse() for reference in param_first_reference if
                    int(reference.element) in param_second_lines], \
                   [reference.reverse() for reference in param_second_reference]
        param_first_lines: List[int] = self.stmt_table.get_statement_line_by_type_name(param_first)
        if param_second == 'STMT':
            param_first_reference: List[Reference] = list(filter(lambda reference: reference,
                                                                 sum([self.parent_table.get_child(line) for line in
                                                                      param_first_lines], [])))
            param_second_reference: List[Reference] = list(filter(lambda reference: reference,
                                                                  [self.parent_table.get_parent(line) for line in
                                                                   self.stmt_table.get_all_statement_lines()]))
            return [reference.reverse() for reference in param_first_reference], [reference.reverse() for reference
                                                                                  in param_second_reference if int(
                    reference.element) in param_first_lines]
        else:
            param_second_lines: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
            return [reference.reverse() for reference in list(filter(lambda reference: reference,
                                                                     sum([self.parent_table.get_child(line) for line in
                                                                          param_first_lines], []))) if
                    int(reference.element) in param_second_lines] \
                , [reference.reverse() for reference in list(filter(lambda reference: reference,
                                                                    [self.parent_table.get_parent(line) for line
                                                                     in param_second_lines])) if
                   int(reference.element) in param_first_lines]

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[Reference]:
        if param_second == '_':
            if param_first == 'STMT':
                return self.parent_table.get_all_parents()
            else:
                return [Reference(reference.reference, reference.element) for reference in list(
                    filter(lambda line: line, sum([self.parent_table.get_child(int(line)) for line in
                                                   self.stmt_table.get_statement_line_by_type_name(
                                                       param_first)], [])))]
        return self.not_initialized_set_and_value_from_set(param_first, param_second)

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.parent_table.get_parent(int(param_second)))
        return self.parent_table.is_parent(int(param_first), int(param_second))

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[Reference]:
        if param_first == '_':
            if param_second == 'STMT':
                return self.parent_table.get_all_children()
            return [reference.reverse() for reference in list(filter(lambda reference: reference,
                                                                     [self.parent_table.get_parent(int(line)) for line
                                                                      in
                                                                      self.stmt_table.get_statement_line_by_type_name(
                                                                          param_second)]))]
        return self.value_from_set_and_not_initialized_set(param_first, param_second)

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            if param_second == '_':
                return bool(self.parent_table.table.index.tolist() and self.parent_table.table.columns.tolist())
            return bool(self.parent_table.get_parent(int(param_second)))
        if param_second == '_':
            return bool(self.parent_table.get_child(int(param_first)))
        return self.parent_table.is_parent(int(param_first), int(param_second))
