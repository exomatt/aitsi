from typing import Tuple, List

from aitsi_parser.CallsTable import CallsTable
from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.VarTable import VarTable
from pql.Reference import Reference


class CallsRelation:
    statements = ['WHILE', 'IF', 'ASSIGN', 'CALL']

    def __init__(self, calls_table: CallsTable, var_table: VarTable, stmt_table: StatementTable,
                 proc_table: ProcTable) -> None:
        super().__init__()
        self.calls_table: CallsTable = calls_table
        self.var_table: VarTable = var_table
        self.stmt_table: StatementTable = stmt_table
        self.proc_table: ProcTable = proc_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        return self.calls_table.is_calls(param_first, param_second)

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[Reference]:
        return self.calls_table.get_called_from(param_first)

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.calls_table.get_called_from(param_first))
        return self.calls_table.is_calls(param_first, param_second)

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[Reference]:
        return self.calls_table.get_calls(param_second)

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> Tuple[
        List[Reference], List[Reference]]:
        return self.calls_table.get_all_procedures_with_procedures_they_calls(), \
               self.calls_table.get_all_procedures_with_procedures_they_are_called_from()

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[Reference]:
        if param_second == '_':
            return self.calls_table.get_all_procedures_with_procedures_they_calls()
        return self.calls_table.get_calls(param_second)

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.calls_table.get_calls(param_second))
        return self.calls_table.is_calls(param_first, param_second)

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[Reference]:
        if param_first == '_':
            return self.calls_table.get_all_procedures_with_procedures_they_are_called_from()
        return self.calls_table.get_called_from(param_first)

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            if param_second == '_':
                return bool(self.calls_table.table.index.tolist() and self.calls_table.table.columns.tolist())
            return bool(self.calls_table.get_calls(param_second))
        if param_second == '_':
            return bool(self.calls_table.get_called_from(param_first))
        return self.calls_table.is_calls(param_first, param_second)
