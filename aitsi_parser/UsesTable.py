from typing import List

import pandas as pd

from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from pql.Reference import Reference


class UsesTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame()
        self.table: pd.DataFrame = table

    def set_uses(self, var_name: str, stmt: str) -> None:
        if stmt not in self.table.columns.tolist():
            self.table[stmt] = 0
        if var_name not in self.table.index.tolist():
            self.table.loc[var_name] = 0
        self.table.loc[var_name, stmt] = 1

    def set_uses_from_procedure(self, called_from: str, called_to: str) -> None:
        try:
            self.table.loc[self.table[called_to] == 1, called_from] = 1
        except Exception:
            pass

    def get_used(self, stmt: str) -> List[Reference]:
        try:
            return [Reference(index, stmt) for index in
                    self.table.index[self.table[str(stmt)] == 1].tolist()]
        except Exception:
            return []

    def get_uses(self, var_name: str) -> List[Reference]:
        try:
            return [Reference(column, var_name) for column in
                    self.table.columns[self.table.loc[var_name] == 1].tolist()]
        except Exception:
            return []

    def get_all_procedures_with_variables_they_use(self, proc_table: ProcTable):
        return sum([self.get_used(proc) for proc in
                    list(set(proc_table.get_all_proc_name()).intersection(
                        self.table.columns.tolist()))], [])

    def get_all_variables_with_procedures_they_are_used(self):
        return sum([self.get_uses(procedure) for procedure in self.table.index.tolist()], [])

    def get_all_stmts_with_variables_they_use(self, stmt_table: StatementTable):
        return sum([self.get_used(str(stmt)) for stmt in list(
            set(stmt_table.get_all_statement_lines()).intersection(
                [int(value) for value in self.table.columns.tolist() if str(value).isdigit()]))], [])

    def get_all_variables_with_stmts_they_are_used(self):
        return sum([self.get_uses(stmt) for stmt in self.table.index.tolist()], [])

    def get_all_stmts_with_variables_they_use_by_stmt_type(self, stmt_type: str, stmt_table: StatementTable):
        return sum([self.get_used(str(stmt)) for stmt in list(
            set(stmt_table.get_statement_line_by_type_name(stmt_type)).intersection(
                [int(value) for value in self.table.columns.tolist() if str(value).isdigit()]))], [])

    def is_used(self, stmt: str, var_name: str) -> bool:
        try:
            return bool(self.table.at[var_name, stmt])
        except Exception:
            return False

    def to_string(self) -> None:
        print("UsesTable:")
        print(self.table.to_string())

    def to_log(self) -> str:
        return "UsesTable: \n" + self.table.to_string()
