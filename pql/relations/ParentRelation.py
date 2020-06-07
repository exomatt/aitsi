from typing import List, Set, Tuple

from aitsi_parser.ParentTable import ParentTable
from aitsi_parser.StatementTable import StatementTable


class ParentRelation:
    statements = ['WHILE', 'IF', 'CALL', 'ASSIGN']

    def __init__(self, parent_table: ParentTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.parent_table: ParentTable = parent_table
        self.stmt_table: StatementTable = stmt_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        return self.parent_table.is_parent(int(param_first), int(param_second))

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[int]:
        if param_second == 'STMT':
            return self.parent_table.get_child(int(param_first))
        return list(set(self.parent_table.get_child(int(param_first)))
                    .intersection(self.stmt_table.get_statement_line_by_type_name(param_second)))

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.parent_table.get_child(int(param_first)))
        return self.parent_table.is_parent(int(param_first), int(param_second))

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[int]:
        if param_first == 'STMT':
            return [self.parent_table.get_parent(int(param_second))]
        return list({self.parent_table.get_parent(int(param_second))}
                    .intersection(self.stmt_table.get_statement_line_by_type_name(param_first)))

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Tuple[List[int], List[int]]:
        if param_first == 'STMT':
            if param_second == 'STMT':
                return self.parent_table.table.index.tolist(), self.parent_table.table.columns.tolist()
            param_second_lines: List[int] = list(
                set(self.stmt_table.get_statement_line_by_type_name(param_second)).intersection(
                    set(self.parent_table.table.columns.tolist())))
            return list(filter(lambda line: line is not None,
                               [self.parent_table.get_parent(int(line)) for line in param_second_lines])), \
                   param_second_lines
        param_first_lines: List[int] = list(set(self.stmt_table.get_statement_line_by_type_name(param_first))
                                            .intersection(self.parent_table.table.index.tolist()))
        if param_second == 'STMT':
            result_second: Set[int] = set()
            for line in param_first_lines:
                result_second.update(self.parent_table.get_child(line))
            return param_first_lines, list(result_second)
        param_second_lines: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
        result_first: List[int] = []
        result_second: Set[int] = set()
        for line in param_first_lines:
            pom: List[int] = list(
                set(self.parent_table.get_child(line)).intersection(set(param_second_lines)))
            if pom:
                result_first.append(line)
                result_second.update(pom)
        return result_first, list(result_second)

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[int]:
        if param_second == '_':
            if param_first == 'STMT':
                return self.parent_table.table.index.tolist()
            return list(set(self.parent_table.table.index.tolist())
                        .intersection(self.stmt_table.get_statement_line_by_type_name(param_first)))
        if param_first == 'STMT':
            return list(filter(lambda line: line is not None, list({self.parent_table.get_parent(int(param_second))})))
        return list({self.parent_table.get_parent(int(param_second))}
                    .intersection(self.stmt_table.get_statement_line_by_type_name(param_first)))

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.parent_table.get_parent(int(param_second)))
        return self.parent_table.is_parent(int(param_first), int(param_second))

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[int]:
        if param_first == '_':
            if param_second == 'STMT':
                return self.parent_table.table.columns.tolist()
            return list(set(self.parent_table.table.columns.tolist())
                        .intersection(self.stmt_table.get_statement_line_by_type_name(param_second)))
        if param_second == 'STMT':
            return self.parent_table.get_child(int(param_first))
        return list(set(self.parent_table.get_child(int(param_first)))
                    .intersection(self.stmt_table.get_statement_line_by_type_name(param_second)))

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            if param_second == '_':
                return bool(self.parent_table.table.index.tolist() and self.parent_table.table.columns.tolist())
            return bool(self.parent_table.get_parent(int(param_second)))
        if param_second == '_':
            return bool(self.parent_table.get_child(int(param_first)))
        return self.parent_table.is_parent(int(param_first), int(param_second))
