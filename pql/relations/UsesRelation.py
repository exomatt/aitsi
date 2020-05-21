from typing import Union, List, Set, Tuple

from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.UsesTable import UsesTable
from aitsi_parser.VarTable import VarTable


class UsesRelation:
    statements = ['WHILE', 'IF', 'ASSIGN', 'CALL']

    def __init__(self, uses_table: UsesTable, var_table: VarTable, stmt_table: StatementTable,
                 proc_table: ProcTable) -> None:
        super().__init__()
        self.uses_table: UsesTable = uses_table
        self.var_table: VarTable = var_table
        self.stmt_table: StatementTable = stmt_table
        self.proc_table: ProcTable = proc_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        return self.uses_table.is_used(param_second, param_first)

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[str]:
        return self.uses_table.get_used(param_first)

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.uses_table.get_used(param_first))
        return self.uses_table.is_used(param_first, param_second)

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> Union[
        List[str], List[int]]:
        if param_first == 'PROCEDURE':
            return [value for value in self.proc_table.get_all_proc_name() if
                    self.uses_table.is_used(value, param_second)]
        if param_first == 'STMT':
            return [value for value in self.stmt_table.get_all_statement_lines() if
                    self.uses_table.is_used(str(value), param_second)]
        return [value for value in self.stmt_table.get_statement_line_by_type_name(param_first) if
                self.uses_table.is_used(str(value), param_second)]

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Union[Tuple[List[str], List[str]], Tuple[List[int], List[str]]]:
        if param_first == 'PROCEDURE':
            return list(set(self.proc_table.get_all_proc_name())
                        .intersection(self.uses_table.table.columns.tolist())), \
                   self.uses_table.table.index.tolist()
        else:
            if param_first == 'STMT':
                return list(set(self.stmt_table.get_all_statement_lines())
                    .intersection(
                    [int(value) for value in self.uses_table.table.columns.tolist() if str(value).isdigit()])), \
                       self.uses_table.table.index.tolist()
            else:
                lines: List[int] = list(set(self.stmt_table.get_statement_line_by_type_name(param_first))
                    .intersection(
                    [int(value) for value in self.uses_table.table.columns.tolist() if str(value).isdigit()]))
                var_name: Set[str] = set()
                for line in lines:
                    var_name.update(self.uses_table.get_used(line))
                return lines, list(var_name)

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> Union[
        List[str], List[int]]:
        if param_first == 'PROCEDURE':
            if param_second == '_':
                return list(set(self.proc_table.get_all_proc_name())
                            .intersection(self.uses_table.table.columns.tolist()))
            return [value for value in self.proc_table.get_all_proc_name() if
                    self.uses_table.is_used(value, param_second)]
        if param_second == '_':
            if param_first == 'STMT':
                return list(set(map(str, self.stmt_table.get_all_statement_lines()))
                            .intersection(self.uses_table.table.columns.tolist()))
            return list(set(map(str, self.stmt_table.get_statement_line_by_type_name(param_first)))
                        .intersection(self.uses_table.table.columns.tolist()))
        if param_first == 'STMT':
            return [value for value in self.stmt_table.get_all_statement_lines() if
                    self.uses_table.is_used(str(value), param_second)]
        return [value for value in self.stmt_table.get_statement_line_by_type_name(param_first) if
                self.uses_table.is_used(str(value), param_second)]

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.uses_table.table.index.tolist())
        return self.uses_table.is_used(param_second, param_first)

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[str]:
        if param_first == '_':
            return self.uses_table.table.index.tolist()
        return self.uses_table.get_used(param_first)

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            if param_second == '_':
                return bool(self.uses_table.table.index.tolist() and self.uses_table.table.columns.tolist())
            return bool(self.uses_table.get_uses(param_second))
        if param_second == '_':
            return bool(self.uses_table.get_used(param_first))
        return self.uses_table.is_used(param_first, param_second)
