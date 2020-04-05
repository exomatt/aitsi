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

    def uses(self, param_first: str, param_second: str) -> Union[Tuple[bool, None],
                                                                 Tuple[List[int], List[str]],
                                                                 Tuple[List[str], None],
                                                                 Tuple[List[int], None],
                                                                 Tuple[List[str], List[str]]]:
        if param_first.isdigit():
            if param_second == '_':
                # p1 - numer linii | p2 - '_'   #Uses(4,"_")
                return self.uses_table.get_used(param_first), None
            elif param_second == 'VARIABLE':
                # p1 - numer linii | p2 - zmienna jakaś
                return self.uses_table.get_used(param_first), None
            else:
                # p1 - numer linii | p2 - zmienna konkretna (np. "x")
                return self.uses_table.is_used(param_second, param_first), None
        elif param_first == '_':
            if param_second == '_':
                # p1 - '_' | p2 - '_'    #Uses(4,"_")
                return self.uses_table.table.index.tolist(), self.uses_table.table.columns.tolist()
            elif param_second == 'VARIABLE':
                # p1 - '_' | p2 - zmienna jakaś
                return self.uses_table.table.index.values, self.uses_table.table.columns.tolist()
            else:
                # p1 - '_' | p2 - zmienna konkretna (np. "x")
                return self.uses_table.get_uses(param_second), None
        elif param_first == 'PROCEDURE':
            if param_second == '_':
                # p1 - p | p2 - '_'
                return self._procedure_and_wildcard()
            elif param_second == 'VARIABLE':
                # p1 - p | p2 - v
                return self._procedure_and_wildcard()
            else:
                # p1 - p | p2 - np. "x"
                return self._procedure_and_variable_name(param_second), None
        else:
            if param_second == '_':
                # p1 - statement | p2 - '_'
                return self._str_type_and_wildcard(param_first)
            elif param_second == 'VARIABLE':
                # p1 - statement | p2 - zmienna jakaś
                return self._str_type_and_wildcard(param_first)
            else:
                # p1 - statement | p2 - zmienna konkretna (np. "x")
                return self._str_type_and_variable_name(param_first, param_second)
        pass

    def _procedure_and_wildcard(self) -> Tuple[List[str], List[str]]:
        result_left: Set[str] = set()
        result_right: Set[str] = set()
        proc_names: List[str] = self.proc_table.get_all_proc_name()
        variables: List[str] = self.var_table.table['variable_name'].tolist()
        for variable in variables:
            for proc_name in proc_names:
                if self.uses_table.is_used(variable, proc_name):
                    result_right.add(variable)
                    result_left.add(proc_name)
        return list(result_left), list(result_right)

    def _procedure_and_variable_name(self, var_name: str) -> List[str]:
        proc_names: List[str] = self.proc_table.get_all_proc_name()
        result: Set[str] = set()
        for proc_name in proc_names:
            if self.uses_table.is_used(var_name, proc_name):
                result.add(proc_name)
        return list(result)

    def _str_type_and_variable_name(self, param_first, param_second) -> Union[Tuple[List[int], None],
                                                                              Tuple[List[str], None],
                                                                              Tuple[bool, None]]:
        lines_by_type_name: List[int] = []
        result_right: Set[str] = set()
        result_left: Set[int] = set()

        if param_first in self.statements:  # IF, WHILE, CALL, ASSIGN
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_first))
            for line_number in lines_by_type_name:
                if self.uses_table.is_used(param_second, str(line_number)):
                    result_left.add(line_number)
            return list(result_left), None

        elif param_first == 'STMT':
            line_numbers: List[int] = self.stmt_table.get_all_statement_lines()
            for line_number in line_numbers:
                if self.uses_table.is_used(param_second, str(line_number)):
                    result_left.add(line_number)
            return list(result_left), None

        else:  # NAZWA PROCEDURY np. "First"
            return self.uses_table.is_used(param_second, param_first), None

    def _str_type_and_wildcard(self, param_first) -> Union[Tuple[List[int], List[str]],
                                                           Tuple[List[str], None]]:
        lines_by_type_name: List[int] = []
        result_right: Set[str] = set()
        result_left: Set[int] = set()

        if param_first in self.statements:  # IF, WHILE, CALL, ASSIGN
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_first))
            variables: List[str] = self.var_table.table['variable_name'].tolist()
            for line_number in lines_by_type_name:
                for variable in variables:
                    if self.uses_table.is_used(variable, str(line_number)):
                        result_left.add(line_number)
                        result_right.add(variable)
            return list(result_left), list(result_right)

        elif param_first == 'STMT':
            line_numbers: List[int] = self.stmt_table.get_all_statement_lines()
            variables: List[str] = self.var_table.table['variable_name'].tolist()
            for line_number in line_numbers:
                for variable in variables:
                    if self.uses_table.is_used(variable, str(line_number)):
                        result_left.add(line_number)
                        result_right.add(variable)
            return list(result_left), list(result_right)

        else:  # NAZWA PROCEDURY np. "First"
            return self.uses_table.get_used(param_first), None
