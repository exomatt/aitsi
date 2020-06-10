from typing import Union, List, Set, Tuple

from aitsi_parser.ModifiesTable import ModifiesTable
from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.VarTable import VarTable


class ModifiesRelation:

    def __init__(self, modifies_table: ModifiesTable, var_table: VarTable,
                 stmt_table: StatementTable, proc_table: ProcTable) -> None:
        super().__init__()
        self.modifies_table: ModifiesTable = modifies_table
        self.var_table: VarTable = var_table
        self.stmt_table: StatementTable = stmt_table
        self.proc_table: ProcTable = proc_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        return self.modifies_table.is_modified(str(param_first), str(param_second))

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[str]:
        return self.modifies_table.get_modified(param_first)

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_second == '_':
            return bool(self.modifies_table.get_modified(param_first))
        return self.modifies_table.is_modified(str(param_first), str(param_second))

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> Union[
        List[str], List[int]]:
        if param_first == 'PROCEDURE':
            return [value for value in self.proc_table.get_all_proc_name() if
                    self.modifies_table.is_modified(str(value), str(param_second))]
        if param_first == 'STMT':
            return [value for value in self.stmt_table.get_all_statement_lines() if
                    self.modifies_table.is_modified(str(value), str(param_second))]
        return [value for value in self.stmt_table.get_statement_line_by_type_name(param_first) if
                self.modifies_table.is_modified(str(value), str(param_second))]

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Union[Tuple[List[str], List[str]], Tuple[List[int], List[str]]]:
        if param_first == 'PROCEDURE':
            return list(set(self.proc_table.get_all_proc_name())
                        .intersection(self.modifies_table.get_all_columns())), \
                   self.modifies_table.get_all_index()
        else:
            if param_first == 'STMT':
                return list(set(self.stmt_table.get_all_statement_lines())
                    .intersection(
                    [int(value) for value in self.modifies_table.get_all_columns() if str(value).isdigit()])), \
                       self.modifies_table.get_all_index()
            else:
                lines: List[int] = list(set(self.stmt_table.get_statement_line_by_type_name(param_first))
                    .intersection(
                    [int(value) for value in self.modifies_table.get_all_columns() if str(value).isdigit()]))
                var_name: Set[str] = set()
                for line in lines:
                    var_name.update(self.modifies_table.get_modified(line))
                return lines, list(var_name)

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> Union[
        List[str], List[int]]:
        if param_first == 'PROCEDURE':
            if param_second == '_':
                return list(set(self.proc_table.get_all_proc_name())
                            .intersection(self.modifies_table.get_all_columns()))
            return [value for value in self.proc_table.get_all_proc_name() if
                    self.modifies_table.is_modified(str(value), str(param_second))]
        if param_second == '_':
            if param_first == 'STMT':
                return list(set(map(str, self.stmt_table.get_all_statement_lines()))
                            .intersection(self.modifies_table.get_all_columns()))
            return list(set(map(str, self.stmt_table.get_statement_line_by_type_name(param_first)))
                        .intersection(self.modifies_table.get_all_columns()))
        if param_first == 'STMT':
            return [value for value in self.stmt_table.get_all_statement_lines() if
                    self.modifies_table.is_modified(str(value), str(param_second))]
        return [value for value in self.stmt_table.get_statement_line_by_type_name(param_first) if
                self.modifies_table.is_modified(str(value), str(param_second))]

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            return bool(self.modifies_table.get_all_index())
        return self.modifies_table.is_modified(str(param_first), str(param_second))

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[str]:
        if param_first == '_':
            return self.modifies_table.get_all_index()
        return self.modifies_table.get_modified(param_first)

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        if param_first == '_':
            if param_second == '_':
                return bool(self.modifies_table.get_all_index() and self.modifies_table.get_all_columns())
            return bool(self.modifies_table.get_modifies(param_second))
        if param_second == '_':
            return bool(self.modifies_table.get_modified(param_first))
        return self.modifies_table.is_modified(str(param_first), str(param_second))
