from typing import List, Union, Set, Tuple

from aitsi_parser.ParentTable import ParentTable
from aitsi_parser.StatementTable import StatementTable
from pql.Reference import Reference


class ParentTRelation:

    def __init__(self, parent_table: ParentTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.parent_table: ParentTable = parent_table
        self.stmt_table: StatementTable = stmt_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        return bool(int(param_second) in self.get_all_lines_in_stmt_lst_child_line(int(param_first)))

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[Reference]:
        if param_second == 'STMT':
            return [Reference(line, param_first) for line in
                    self.get_all_lines_in_stmt_lst_child_line(int(param_first))]
        return [Reference(line, param_first) for line in list(
            set(self.get_all_lines_in_stmt_lst_child_line(int(param_first))).intersection(
                self.stmt_table.get_statement_line_by_type_name(param_second)))]

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.parent_table.get_child(int(param_first)))
        return bool(int(param_second) in self.get_all_lines_in_stmt_lst_child_line(int(param_first)))

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[Reference]:
        if param_first == 'STMT':
            return [Reference(line, param_second) for line in
                    self.get_all_lines_in_stmt_lst_parent_line(int(param_second))]
        return [Reference(line, param_second) for line in
                set(self.get_all_lines_in_stmt_lst_parent_line(int(param_second))).intersection(
                    self.stmt_table.get_statement_line_by_type_name(param_first))]

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Tuple[List[Reference], List[Reference]]:
        if param_first == 'STMT':
            if param_second == 'STMT':
                return self.parent_table.get_all_parents(), self.parent_table.get_all_children()
            else:
                pom_second: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
                return [Reference(line_first, line) for line in pom_second for line_first in
                        self.get_all_lines_in_stmt_lst_parent_line(line)], \
                       [Reference(line, line_first) for line in pom_second for line_first in
                        self.get_all_lines_in_stmt_lst_parent_line(line)]
        else:
            param_first_lines: List[int] = self.stmt_table.get_statement_line_by_type_name(param_first)
            if param_second == 'STMT':
                result_first: Set[Reference] = set()
                result_second: Set[Reference] = set()
                for line in param_first_lines:
                    pom: List[Reference] = [Reference(line_after, line) for line_after in
                                            self.get_all_lines_in_stmt_lst_child_line(line)]
                    result_first.update([Reference(reference.reference, reference.element) for reference in pom])
                    result_second.update(pom)
                return list(result_first), list(result_second)
            else:
                param_second_lines: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
                return [Reference(line, line_second) for line in param_first_lines for line_second in
                        self.get_all_lines_in_stmt_lst_child_line(line) if line_second in param_second_lines] \
                    , [Reference(line, line_first) for line in param_second_lines for line_first in
                       self.get_all_lines_in_stmt_lst_parent_line(line) if line_first in param_first_lines]

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[Reference]:
        if param_second == '_':
            if param_first == 'STMT':
                return self.parent_table.get_all_parents()
            return [reference.reverse() for reference in list(filter(lambda reference: reference,
                                                                     sum([self.parent_table.get_child(int(line)) for
                                                                          line
                                                                          in
                                                                          self.stmt_table.get_statement_line_by_type_name(
                                                                              param_first)], [])))]
        return self.not_initialized_set_and_value_from_set(param_first, param_second)

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.parent_table.get_parent(int(param_second)))
        return self.value_from_set_and_value_from_set(param_first, param_second)

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[Reference]:
        if param_first == '_':
            if param_second == 'STMT':
                return self.parent_table.get_all_children()
            return [reference.reverse() for reference in
                    list(filter(lambda reference: reference, [self.parent_table.get_parent(int(line)) for line in
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
        return bool(int(param_second) in self.get_all_lines_in_stmt_lst_child_line(int(param_first)))

    def get_all_lines_in_stmt_lst_parent_line(self, line_number: int) -> List[int]:
        pom: Union[Reference, None] = self.parent_table.get_parent(int(line_number))
        results: List[int] = []
        while pom is not None:
            results.append(int(pom.element))
            pom = self.parent_table.get_parent(int(pom.element))
        return results

    def get_all_lines_in_stmt_lst_child_line(self, line_number: int) -> List[int]:
        result: Set[int] = set()
        pom: List[Reference] = self.parent_table.get_child(int(line_number))
        for child in pom:
            new_previous: Set[Reference] = set(self.parent_table.get_child(int(child.element)))
            if not new_previous.issubset(pom):
                pom.extend(new_previous)
            result.add(int(child.element))
        return list(result)
