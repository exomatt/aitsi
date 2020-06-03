from typing import Union, Tuple, List, Set

from aitsi_parser.FollowsTable import FollowsTable
from aitsi_parser.StatementTable import StatementTable
from pql.Reference import Reference


class FollowsTRelation:

    def __init__(self, follows_table: FollowsTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.stmt_table: StatementTable = stmt_table
        self.follows_table: FollowsTable = follows_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        return bool(int(param_second) in self.get_all_lines_in_stmt_lst_after_line(int(param_first)))

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[Reference]:
        if param_second == 'STMT':
            return list(set([self.follows_table.get_follows(int(line)) for line in
                             self.get_all_lines_in_stmt_lst_after_line(int(param_first))]).intersection(
                self.follows_table.get_all_follows()))
        return [self.follows_table.get_follows(int(line)) for line in list(
            set(self.get_all_lines_in_stmt_lst_after_line(int(param_first))).intersection(
                self.stmt_table.get_statement_line_by_type_name(param_second)))]

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.follows_table.get_child(int(param_first)))
        return bool(int(param_second) in self.get_all_lines_in_stmt_lst_after_line(int(param_first)))

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[Reference]:
        if param_first == 'STMT':
            return list(filter(lambda reference: reference, [self.follows_table.get_follows(int(param_second))]))
        reference: Reference = self.follows_table.get_follows(int(param_second))
        if reference:
            return [reference] if int(reference.element) in list(
                set(self.get_all_lines_in_stmt_lst_before_line(int(param_second))).intersection(
                    self.stmt_table.get_statement_line_by_type_name(param_first))) else []
        return []

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Tuple[List[Reference], List[Reference]]:
        if param_first == 'STMT':
            if param_second == 'STMT':
                return self.follows_table.get_all_children(), self.follows_table.get_all_follows()
            else:
                pom_second: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
                result_first: Set[Reference] = set()
                result_second: Set[Reference] = set()
                for line in pom_second:
                    pom: List[Reference] = list(filter(lambda reference: reference,
                                                       [self.follows_table.get_follows(int(line_before)) for line_before
                                                        in self.get_all_lines_in_stmt_lst_before_line(line)]))
                    result_first.update(pom)
                    result_second.update([Reference(reference.reference, reference.element) for reference in pom])
                return list(result_first), list(result_second)
        else:
            pom_first: List[int] = self.stmt_table.get_statement_line_by_type_name(param_first)
            if param_second == 'STMT':
                result_first: Set[Reference] = set()
                result_second: Set[Reference] = set()
                for line in pom_first:
                    pom: List[Reference] = list(filter(lambda reference: reference,
                                                       [self.follows_table.get_child(int(line_after)) for line_after in
                                                        self.get_all_lines_in_stmt_lst_after_line(line)]))
                    result_first.update([Reference(reference.reference, reference.element) for reference in pom])
                    result_second.update(pom)
                return list(result_first), list(result_second)
            else:
                pom_second: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
                result_first: Set[Reference] = set()
                result_second: Set[Reference] = set()
                for line in pom_first:
                    pom: List[Reference] = list(filter(lambda reference: reference,
                                                       [self.follows_table.get_child(int(line_after)) for line_after in
                                                        list(
                                                            set(self.get_all_lines_in_stmt_lst_after_line(
                                                                line)).intersection(set(pom_second)))]))
                    result_first.update([Reference(reference.reference, reference.element) for reference in pom])
                    result_second.update(pom)
                return list(result_first), list(result_second)

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[Reference]:
        if param_second == '_':
            if param_first == 'STMT':
                return self.follows_table.get_all_children()
            return [self.follows_table.get_follows(int(line)) for line in
                    list(set(self.stmt_table.get_statement_line_by_type_name(param_first)).intersection(
                        self.follows_table.table.index.tolist()))]
        return self.not_initialized_set_and_value_from_set(param_first, param_second)

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.follows_table.get_follows(int(param_second)))
        return self.value_from_set_and_value_from_set(param_first, param_second)

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[Reference]:
        if param_first == '_':
            if param_second == 'STMT':
                return self.follows_table.get_all_follows()
            return list(filter(lambda reference: reference, [self.follows_table.get_child(int(line)) for line in
                                                             self.stmt_table.get_statement_line_by_type_name(
                                                                 param_second)]))
        return self.value_from_set_and_not_initialized_set(param_first, param_second)

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            if param_second == '_':
                return bool(self.follows_table.table.index.tolist() and self.follows_table.table.columns.tolist())
            return bool(self.follows_table.get_follows(int(param_second)))
        if param_second == '_':
            return bool(self.follows_table.get_child(int(param_first)))
        return bool(int(param_second) in self.get_all_lines_in_stmt_lst_after_line(int(param_first)))

    def get_all_lines_in_stmt_lst_before_line(self, line_number: int) -> List[int]:
        pom: Union[Reference, None] = self.follows_table.get_follows(int(line_number))
        results: List[int] = []
        while pom is not None:
            results.append(int(pom.element))
            pom = self.follows_table.get_follows(int(pom.element))
        return results

    def get_all_lines_in_stmt_lst_after_line(self, line_number: int) -> List[int]:
        pom: Union[Reference, None] = self.follows_table.get_child(int(line_number))
        results: List[int] = []
        while pom is not None:
            results.append(int(pom.element))
            pom = self.follows_table.get_child(int(pom.element))
        return results
