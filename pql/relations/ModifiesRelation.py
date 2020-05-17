from typing import Union, List, Set, Dict, Tuple

from aitsi_parser.ModifiesTable import ModifiesTable
from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.VarTable import VarTable


class ModifiesRelation:
    statements = ['WHILE', 'IF', 'ASSIGN']

    def __init__(self, modifies_table: ModifiesTable, var_table: VarTable,
                 stmt_table: StatementTable, proc_table: ProcTable) -> None:
        super().__init__()
        self.modifies_table: ModifiesTable = modifies_table
        self.var_table: VarTable = var_table
        self.stmt_table: StatementTable = stmt_table
        self.proc_table: ProcTable = proc_table

    def modifies(self, param_first: str, param_second: str) -> Union[Tuple[bool, None],
                                                                     Tuple[List[int], List[str]],
                                                                     Tuple[List[str], None],
                                                                     Tuple[List[int], None],
                                                                     Tuple[List[str], List[str]]]:
        if param_first.isdigit():
            if param_second == 'VARIABLE':
                # p1 jest liczba, a p2 zmienna variable v czyli   np. 'VARIABLE' Modifies('3',v) zwraca liste ze zmiennymi modyfikowanymi tam lub pusta liste
                return self._digit_and_wild_card_or_variable(param_first)
            elif param_second == '_':
                # p1 jest liczba, a p2 zmienna wild card  np. '_' zwraca liste ze zmiennymi modyfikowanymi tam lub pusta liste
                return self._digit_and_wild_card_or_variable(param_first)
            else:
                # p1 jest liczba, a p2 zmienna variable np. 'x' zwraca True jezeli w danej lini jest zmienna modyfikowana
                return self.modifies_table.is_modified(param_second, param_first), None
        elif param_first == '_':
            if param_second == '_':
                # p1 jest '_', a p2 zmienna variable np.  variable v Modifies('_', '_')
                return self.modifies_table.table.index.tolist(), self.modifies_table.table.columns.tolist()
            elif param_second == 'VARIABLE':
                # p1 jest '_', a p2 zmienna variable np.  variable v Modifies('_', v) zwraca nazwy zmiennych   ktore sa modyfikowane gdziekolwiek
                return self.var_table.table['variable_name'].tolist(), None
            else:
                # p1 jest '_', a p2 zmienna variable np. 'x' zwraca numery lini    gdzie jest modyfikowanea zmienna o nazwie x
                return self.modifies_table.get_modifies(param_second), None
        else:
            if param_second == '_':
                # p1 jest stmt np 'IF', a p2  '_'   przypadek skrajny Modifies('IF',_)
                return self._str_type_wildcard(param_first)
            elif param_second == 'VARIABLE':
                # np. 'VARIABLE' Modifies('IF',v)
                return self._str_type_variable(param_first)
            else:
                # p1 jest stmt np 'IF', a p2 zmienna variable np. 'x' zwracamy numer lini tego ifa, oraz numer lini modyfikacji x
                return self._str_type_var_name(param_first, param_second)

    def _str_type_var_name(self, param_first, param_second) -> Tuple[List[int], None]:
        lines_by_type_name: List[int] = []
        result_left: Set[int] = set()
        if param_first == 'CALL':
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name('CALL'))
            for line in lines_by_type_name:
                other_info: Dict[str][str] = self.stmt_table.get_other_info(line)
                if self.modifies_table.is_modified(param_second, other_info['value']):
                    result_left.add(line)
        elif param_first == 'STMT':
            for stmt in self.statements:
                lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
            for line in lines_by_type_name:
                if self.modifies_table.is_modified(param_second, str(line)):
                    result_left.add(line)
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name('CALL'))
            for line in lines_by_type_name:
                other_info: Dict[str][str] = self.stmt_table.get_other_info(line)
                if self.modifies_table.is_modified(param_second, other_info['value']):
                    result_left.add(line)

        elif param_first in self.statements:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_first))
            for line in lines_by_type_name:
                if self.modifies_table.is_modified(param_second, str(line)):
                    result_left.add(line)
        else:
            # procedura jak 1 parametr
            result_left: Set[str] = set()
            if param_first == 'PROCEDURE':
                proc_names: List[str] = self.proc_table.get_all_proc_name()
                for proc_name in proc_names:
                    if self.modifies_table.is_modified(param_second, proc_name):
                        result_left.add(proc_name)
            else:
                # nazwa procedury
                variables: List[str] = self.var_table.table['variable_name'].tolist()
                if self.modifies_table.is_modified(param_second, param_first):
                    result_left.add(param_first)
        return list(result_left), None

    def _str_type_wildcard(self, param_first) -> Union[
        Tuple[List[int], None], Tuple[List[str], None], Tuple[bool, None]]:
        lines_by_type_name: List[int] = []
        result_right: Set[str] = set()
        result_left: Set[int] = set()
        if param_first == 'CALL':
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name('CALL'))
            variables: List[str] = self.var_table.table['variable_name'].tolist()
            for line in lines_by_type_name:
                other_info: Dict[str][str] = self.stmt_table.get_other_info(line)
                for variable in variables:
                    if self.modifies_table.is_modified(variable, other_info['value']):
                        result_left.add(line)
        elif param_first == 'STMT':
            variables: List[str] = self.var_table.table['variable_name'].tolist()
            for variable in variables:
                result_left.update([line for line in self.modifies_table.get_modifies(variable) if line.isdigit()])
        elif param_first in self.statements:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_first))
            for line in lines_by_type_name:
                result_right.update(self.modifies_table.get_modified(str(line)))
                result_left.add(line)
        else:
            # procedura jak 1 parametr
            if param_first == 'PROCEDURE':
                result_left: Set[str] = set()
                proc_names: List[str] = self.proc_table.get_all_proc_name()
                variables: List[str] = self.var_table.table['variable_name'].tolist()
                for proc_name in proc_names:
                    for variable in variables:
                        if self.modifies_table.is_modified(variable, proc_name):
                            result_left.add(proc_name)
                            break
            else:
                # nazwa procedury
                variables: List[str] = self.var_table.table['variable_name'].tolist()
                if not self.proc_table.is_in(param_first):
                    return [], []
                info: Dict[str, int] = self.proc_table.get_other_info(param_first)
                for variable in variables:
                    if self.modifies_table.is_modified(variable, param_first):
                        return True, None
                return False, None
        return list(result_left), None

    def _str_type_variable(self, param_first) -> Union[Tuple[List[int], List[str]], Tuple[List[str], List[str]]]:
        lines_by_type_name: List[int] = []
        result_right: Set[str] = set()
        result_left: Set[int] = set()
        if param_first == 'CALL':
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name('CALL'))
            variables: List[str] = self.var_table.table['variable_name'].tolist()
            for line in lines_by_type_name:
                other_info: Dict[str][str] = self.stmt_table.get_other_info(line)
                for variable in variables:
                    if self.modifies_table.is_modified(variable, other_info['value']):
                        result_right.add(variable)
                        result_left.add(line)
        elif param_first == 'STMT':
            result_right.update(self.modifies_table.get_all_variables())
            result_left.update(self.modifies_table.get_all_lines())
        elif param_first in self.statements:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_first))
            for line in lines_by_type_name:
                result_right.update(self.modifies_table.get_modified(str(line)))
                result_left.add(line)
        else:
            # procedura jak 1 parametr
            if param_first == 'PROCEDURE':
                result_left: Set[str] = set()
                proc_names: List[str] = self.proc_table.get_all_proc_name()
                variables: List[str] = self.var_table.table['variable_name'].tolist()
                for variable in variables:
                    for proc_name in proc_names:
                        if self.modifies_table.is_modified(variable, proc_name):
                            result_right.add(variable)
                            result_left.add(proc_name)
            else:
                # nazwa procedury
                variables: List[str] = self.var_table.table['variable_name'].tolist()
                for variable in variables:
                    if self.modifies_table.is_modified(variable, param_first):
                        result_right.add(variable)
                return list(result_right), None
        return list(result_left), list(result_right)

    def _digit_and_wild_card_or_variable(self, param_first) -> Tuple[List[str], None]:
        result: Set[str] = set()
        variables: List[str] = self.var_table.table['variable_name'].tolist()
        for variable in variables:
            if self.modifies_table.is_modified(variable, param_first):
                result.add(variable)
        return list(result), None
