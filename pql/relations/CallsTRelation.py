from typing import Tuple, List, Set

from aitsi_parser.CallsTable import CallsTable
from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.VarTable import VarTable


class CallsTRelation:
    statements = ['WHILE', 'IF', 'ASSIGN', 'CALL']

    def __init__(self, calls_table: CallsTable, var_table: VarTable, stmt_table: StatementTable,
                 proc_table: ProcTable) -> None:
        super().__init__()
        self.calls_table: CallsTable = calls_table
        self.var_table: VarTable = var_table
        self.stmt_table: StatementTable = stmt_table
        self.proc_table: ProcTable = proc_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == param_second:
            return False
        for procedure in self.calls_table.get_called_from(param_first):
            if procedure == param_second:
                return True
            else:
                return_value = self.value_from_set_and_value_from_set(procedure, param_second)
                if return_value == True:
                    return True
        return False

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[str]:
        result: List[str] = self.calls_table.get_called_from(param_first)
        procedures_to_check: Set[str] = set(self.calls_table.get_called_from(param_first))
        for procedure in procedures_to_check:
            result.extend(self.value_from_set_and_not_initialized_set(procedure, ''))
        return list(set(result))

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.value_from_set_and_not_initialized_set(param_first, ''))
        return self.value_from_set_and_value_from_set(param_first, param_second)

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[str]:
        result: List[str] = self.calls_table.get_calls(param_second)
        procedures_to_check: Set[str] = set(self.calls_table.get_calls(param_second))
        for procedure in procedures_to_check:
            result.extend(self.not_initialized_set_and_value_from_set('', procedure))
        return list(set(result))

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Tuple[List[str], List[str]]:
        return self.calls_table.table.index.tolist(), self.calls_table.table.columns.tolist()

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[str]:
        if param_second == '_':
            return self.calls_table.table.index.tolist()
        return self.not_initialized_set_and_value_from_set('', param_second)

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.not_initialized_set_and_value_from_set('', param_second))
        return self.value_from_set_and_value_from_set(param_first, param_second)

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[str]:
        if param_first == '_':
            return self.calls_table.table.columns.tolist()
        return self.value_from_set_and_not_initialized_set(param_first, '')

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            if param_second == '_':
                return bool(self.calls_table.table.index.tolist() and self.calls_table.table.columns.tolist())
            return bool(self.not_initialized_set_and_value_from_set('', param_second))
        if param_second == '_':
            return bool(self.value_from_set_and_not_initialized_set(param_first, ''))
        return self.value_from_set_and_value_from_set(param_first, param_second)
