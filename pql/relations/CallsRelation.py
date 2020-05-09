from typing import Union, Tuple, List, Set

from aitsi_parser.CallsTable import CallsTable
from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.VarTable import VarTable


class CallsRelation:
    statements = ['WHILE', 'IF', 'ASSIGN', 'CALL']

    def __init__(self, calls_table: CallsTable, var_table: VarTable, stmt_table: StatementTable,
                 proc_table: ProcTable) -> None:
        super().__init__()
        self.calls_table: CallsTable = calls_table
        self.var_table: VarTable = var_table
        self.stmt_table: StatementTable = stmt_table
        self.proc_table: ProcTable = proc_table

    def calls(self, param_first: str, param_second: str) -> Union[Tuple[bool, None],
                                                                  Tuple[List[str], None],
                                                                  Tuple[List[str], List[str]]]:
        if param_first == 'PROCEDURE' or param_first == '_':
            if param_second == 'PROCEDURE':
                # p1 - procedura (p) lub '_' | p2 - procedura (p2)
                return self.calls_table.table.columns.tolist(), self.calls_table.table.index.tolist()
            elif param_second == '_':
                # p1 - procedura (p) lub '_' | p2 - '_' czyli dowolna procedura
                return self.calls_table.table.index.tolist(), self.calls_table.table.columns.tolist()
            else:
                # p1 - procedura (p) lub '_' | p2 - np. "First" czyli konkretna procedura
                return self.calls_table.get_calls(param_second), None
        else:
            if param_second == 'PROCEDURE':
                # p1 - nazwa procedury (np. "First") | p2 - procedura (p2)
                return self.calls_table.get_called_from(param_first), None
            elif param_second == '_':
                # p1 - nazwa procedury (np. "First") | p2 - '_' czyli dowolna procedura
                return self.calls_table.get_called_from(param_first), None
            else:
                # p1 - nazwa procedury (np. "First") | p2 - np. "First" czyli konkretna procedura
                return self.calls_table.is_calls(param_first, param_second), None

    def calls_T(self, param_first: str, param_second: str) -> Union[Tuple[bool, None],
                                                                    Tuple[List[str], None],
                                                                    Tuple[List[str], List[str]]]:
        if param_first == 'PROCEDURE' or param_first == '_':
            if param_second == 'PROCEDURE':
                # p1 - procedura (p) lub '_' | p2 - procedura (p2)
                return self.calls_table.table.columns.tolist(), self.calls_table.table.index.tolist()
            elif param_second == '_':
                # p1 - procedura (p) lub '_' | p2 - '_' czyli dowolna procedura
                return self.calls_table.table.index.tolist(), self.calls_table.table.columns.tolist()
            else:
                # p1 - procedura (p) lub '_' | p2 - np. "First" czyli konkretna procedura
                return self._wildcard_and_procedure_name(param_second), None
        else:
            if param_second == 'PROCEDURE':
                # p1 - nazwa procedury (np. "First") | p2 - procedura (p2)
                return self._procedure_name_and_wildcard(param_first), None
            elif param_second == '_':
                # p1 - nazwa procedury (np. "First") | p2 - '_' czyli dowolna procedura
                return self._procedure_name_and_wildcard(param_first), None
            else:
                # p1 - nazwa procedury (np. "First") | p2 - np. "First" czyli konkretna procedura
                return self._procedure_name_and_procedure_name(param_first, param_second), None

    def _procedure_name_and_wildcard(self, proc_name: str) -> List[str]:
        result: List[str] = self.calls_table.get_called_from(proc_name)
        procedures_to_check: Set[str] = set(self.calls_table.get_called_from(proc_name))
        for procedure in procedures_to_check:
            result.extend(self._procedure_name_and_wildcard(procedure))
        return list(set(result))

    def _wildcard_and_procedure_name(self, proc_name: str) -> List[str]:
        result: List[str] = self.calls_table.get_calls(proc_name)
        procedures_to_check: Set[str] = set(self.calls_table.get_calls(proc_name))
        for procedure in procedures_to_check:
            result.extend(self._wildcard_and_procedure_name(procedure))
        return list(set(result))

    def _procedure_name_and_procedure_name(self, param_first: str, param_second: str) -> bool:
        for procedure in self.calls_table.get_called_from(param_first):
            if procedure == param_second:
                return True
            else:
                return self._procedure_name_and_procedure_name(param_first, procedure)
        return False
