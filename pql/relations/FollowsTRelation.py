from typing import Union, Tuple, List, Set

from aitsi_parser.FollowsTable import FollowsTable
from aitsi_parser.StatementTable import StatementTable


class FollowsTRelation:
    statements = ['WHILE', 'IF', 'CALL', 'ASSIGN']

    def __init__(self, follows_table: FollowsTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.stmt_table: StatementTable = stmt_table
        self.follows_table: FollowsTable = follows_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        return bool(int(param_second) in self.get_all_lines_in_stmt_lst_after_line(int(param_first)))

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[int]:
        if param_second == 'STMT':
            pom: List[int] = self.follows_table.table.columns.tolist()
        else:
            pom: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
        return list(set(self.get_all_lines_in_stmt_lst_after_line(int(param_first))).intersection(pom))

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.follows_table.get_child(int(param_first)))
        return bool(int(param_second) in self.get_all_lines_in_stmt_lst_after_line(int(param_first)))

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[int]:
        if param_first == 'STMT':
            pom: List[int] = self.follows_table.table.index.tolist()
        else:
            pom: List[int] = self.stmt_table.get_statement_line_by_type_name(param_first)
        return list(set(self.get_all_lines_in_stmt_lst_before_line(int(param_second))).intersection(pom))

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Tuple[List[int], List[int]]:
        if param_first == 'STMT':
            if param_second == 'STMT':
                return self.follows_table.table.index.tolist(), self.follows_table.table.columns.tolist()
            else:
                pom_second: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
                result_first: Set[int] = set()
                result_second: List[int] = []
                for line in pom_second:
                    pom: List[int] = self.get_all_lines_in_stmt_lst_before_line(line)
                    if pom:
                        result_first.update(pom)
                        result_second.append(line)
                return list(result_first), result_second
        else:
            pom_first: List[int] = self.stmt_table.get_statement_line_by_type_name(param_first)
            if param_second == 'STMT':
                result_first: List[int] = []
                result_second: Set[int] = set()
                for line in pom_first:
                    pom: List[int] = self.get_all_lines_in_stmt_lst_after_line(line)
                    if pom:
                        result_first.append(line)
                        result_second.update(pom)
                return result_first, list(result_second)
            else:
                pom_second: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
                result_first: List[int] = []
                result_second: Set[int] = set()
                for line in pom_first:
                    pom: List[int] = list(
                        set(self.get_all_lines_in_stmt_lst_after_line(line)).intersection(set(pom_second)))
                    if pom:
                        result_first.append(line)
                        result_second.update(pom)
                return result_first, list(result_second)

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[int]:
        if param_second == '_':
            if param_first == 'STMT':
                pom: List[int] = self.follows_table.table.index.tolist()
            else:
                pom: List[int] = list(set(self.stmt_table.get_statement_line_by_type_name(param_first)).intersection(
                    self.follows_table.table.index.tolist()))
            return pom
        return self.not_initialized_set_and_value_from_set(param_first, param_second)

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.follows_table.get_follows(int(param_second)))
        return self.value_from_set_and_value_from_set(param_first, param_second)

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[int]:
        if param_first == '_':
            if param_second == 'STMT':
                pom: List[int] = self.follows_table.table.columns.tolist()
            else:
                pom: List[int] = list(set(self.stmt_table.get_statement_line_by_type_name(param_second)).intersection(
                    self.follows_table.table.columns.tolist()))
            return pom
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
        pom: Union[int, None] = self.follows_table.get_follows(int(line_number))
        results: List[int] = []
        while pom is not None:
            results.append(pom)
            pom = self.follows_table.get_follows(pom)
        return results

    def get_all_lines_in_stmt_lst_after_line(self, line_number: int) -> List[int]:
        pom: Union[int, None] = self.follows_table.get_child(int(line_number))
        results: List[int] = []
        while pom is not None:
            results.append(pom)
            pom = self.follows_table.get_child(pom)
        return results
