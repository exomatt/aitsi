from typing import List, Set, Tuple

from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.UsesTable import UsesTable
from aitsi_parser.VarTable import VarTable
from pql.Reference import Reference


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
        return self.uses_table.is_used(param_first, param_second)

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[Reference]:
        return self.uses_table.get_used(param_first)

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.uses_table.get_used(param_first))
        return self.uses_table.is_used(param_first, param_second)

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[Reference]:
        if param_first == 'PROCEDURE':
            return [Reference(value, param_second) for value in self.proc_table.get_all_proc_name() if
                    self.uses_table.is_used(value, param_second)]
        if param_first == 'STMT':
            return [Reference(str(value), param_second) for value in self.stmt_table.get_all_statement_lines() if
                    self.uses_table.is_used(str(value), param_second)]
        return [Reference(str(value), param_second) for value in
                self.stmt_table.get_statement_line_by_type_name(param_first) if
                self.uses_table.is_used(str(value), param_second)]

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> Tuple[
        List[Reference], List[Reference]]:
        if param_first == 'PROCEDURE':
            return [reference.reverse() for reference in
                    self.uses_table.get_all_procedures_with_variables_they_use(self.proc_table)], \
                   [reference.reverse() for reference in
                    self.uses_table.get_all_variables_with_procedures_they_are_used()]
        else:
            if param_first == 'STMT':
                return [reference.reverse() for reference in
                        self.uses_table.get_all_stmts_with_variables_they_use(self.stmt_table)], \
                       [reference.reverse() for reference in
                        self.uses_table.get_all_variables_with_stmts_they_are_used()]
            else:
                lines: List[Reference] = [reference.reverse() for reference in
                                          self.uses_table.get_all_stmts_with_variables_they_use_by_stmt_type(
                                              param_first, self.stmt_table)]
                var_name: Set[Reference] = set()
                for line in lines:
                    var_name.update(self.uses_table.get_used(line.element))
                return lines, list(var_name)

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[Reference]:
        if param_first == 'PROCEDURE':
            if param_second == '_':
                return [reference.reverse() for reference in
                        self.uses_table.get_all_procedures_with_variables_they_use(self.proc_table)]
            return [Reference(value, param_second) for value in self.proc_table.get_all_proc_name() if
                    self.uses_table.is_used(value, param_second)]
        if param_second == '_':
            if param_first == 'STMT':
                return [reference.reverse() for reference in
                        self.uses_table.get_all_stmts_with_variables_they_use(self.stmt_table)]
            return [reference.reverse() for reference in
                    self.uses_table.get_all_stmts_with_variables_they_use_by_stmt_type(param_first, self.stmt_table)]
        if param_first == 'STMT':
            return [Reference(str(value), param_second) for value in self.stmt_table.get_all_statement_lines() if
                    self.uses_table.is_used(str(value), param_second)]
        return [Reference(str(value), param_second) for value in
                self.stmt_table.get_statement_line_by_type_name(param_first) if
                self.uses_table.is_used(str(value), param_second)]

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.uses_table.table.index.tolist())
        return self.uses_table.is_used(param_second, param_first)

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[Reference]:
        if param_first == '_':
            return [reference.reverse() for reference in sum([self.uses_table.get_uses(stmt) for stmt in
                                                              self.uses_table.table.index.tolist()], [])]
        return self.uses_table.get_used(param_first)

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            if param_second == '_':
                return bool(self.uses_table.table.index.tolist() and self.uses_table.table.columns.tolist())
            return bool(self.uses_table.get_uses(param_second))
        if param_second == '_':
            return bool(self.uses_table.get_used(param_first))
        return self.uses_table.is_used(param_first, param_second)
