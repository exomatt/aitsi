from typing import Union, List, Set, Dict

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

    def modifies(self, param_first: str, param_second: str) -> Union[bool, List[str], List[int]]:
        if param_first.isdigit():
            if param_second == 'VARIABLE':
                # p1 jest liczba, a p2 zmienna variable v czyli   np. 'VARIABLE' Modifies('3',v) zwraca liste ze zmiennymi modyfikowanymi tam lub pusta liste
                return self._digit_and_wild_card_or_variable(param_first)
            elif param_second == '_':
                # p1 jest liczba, a p2 zmienna wild card  np. '_' zwraca liste ze zmiennymi modyfikowanymi tam lub pusta liste
                return self._digit_and_wild_card_or_variable(param_first)
            else:
                # p1 jest liczba, a p2 zmienna variable np. 'x' zwraca True jezeli w danej lini jest zmienna modyfikowana
                return self.modifies_table.is_modified(param_second, param_first)
        elif param_first == '_':
            if param_second == '_':
                # p1 jest '_', a p2 zmienna variable np.  variable v Modifies('_', '_')
                return self.var_table.table['variable_name'].tolist()
            elif param_second == 'VARIABLE':
                # p1 jest '_', a p2 zmienna variable np.  variable v Modifies('_', v) zwraca nazwy zmiennych   ktore sa modyfikowane gdziekolwiek
                return self.var_table.table['variable_name'].tolist()
            else:
                # p1 jest '_', a p2 zmienna variable np. 'x' zwraca numery lini    gdzie jest modyfikowanea zmienna o nazwie x
                return self.modifies_table.get_modifies(param_second)
        else:
            if param_second == '_':
                # p1 jest stmt np 'IF', a p2  '_'   przypadek skrajny Modifies('IF',_) zwraca linie gdzie cokolwiek jest modyfikowane
                return self._str_type_wildcard_or_variable(param_first)
            elif param_second == 'VARIABLE':
                # wedlug handbooka to kiedy jest if i while to zwracamy wszystkie modyfikowane  zmienne
                # np. 'VARIABLE' Modifies('IF',v)
                return self._str_type_wildcard_or_variable(param_first)
            else:
                # p1 jest stmt np 'IF', a p2 zmienna variable np. 'x' zwracamy numer lini tego ifa
                return self._str_type_var_name(param_first, param_second)

    def _str_type_var_name(self, param_first, param_second) -> List[int]:
        lines_by_type_name: List[int] = []
        result: Set[int] = set()
        if param_first == 'CALL':
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name('CALL'))
            for line in lines_by_type_name:
                other_info: Dict[str][str] = self.stmt_table.get_other_info(line)
                if self.modifies_table.is_modified(param_second, other_info['value']):
                    result.add(line)
        elif param_first == 'STMT':
            for stmt in self.statements:
                lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
            for line in lines_by_type_name:
                if self.modifies_table.is_modified(param_second, str(line)):
                    result.add(line)
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name('CALL'))
            for line in lines_by_type_name:
                other_info: Dict[str][str] = self.stmt_table.get_other_info(line)
                if self.modifies_table.is_modified(param_second, other_info['value']):
                    result.add(line)

        elif param_first in self.statements:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_first))
            for line in lines_by_type_name:
                if self.modifies_table.is_modified(param_second, str(line)):
                    result.add(line)
        else:
            # procedura jak 1 parametr
            result: Set[str] = set()
            if param_first == 'PROCEDURE':
                proc_names: List[str] = self.proc_table.get_all_proc_name()
                for proc_name in proc_names:
                    if self.modifies_table.is_modified(param_second, proc_name):
                        result.add(proc_name)
            else:
                # nazwa procedury
                variables: List[str] = self.var_table.table['variable_name'].tolist()
                if self.modifies_table.is_modified(param_second, param_first):
                    result.add(param_first)
        return list(result)

    def _str_type_wildcard_or_variable(self, param_first) -> List[str]:
        lines_by_type_name: List[int] = []
        result: Set[str] = set()
        if param_first == 'CALL':
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name('CALL'))
            variables: List[str] = self.var_table.table['variable_name'].tolist()
            for line in lines_by_type_name:
                other_info: Dict[str][str] = self.stmt_table.get_other_info(line)
                for variable in variables:
                    if self.modifies_table.is_modified(variable, other_info['value']):
                        result.add(variable)
        elif param_first == 'STMT':
            for stmt in self.statements:
                lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
            for line in lines_by_type_name:
                result.update(self.modifies_table.get_modified(str(line)))
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name('CALL'))
            variables: List[str] = self.var_table.table['variable_name'].tolist()
            for line in lines_by_type_name:
                other_info: Dict[str][str] = self.stmt_table.get_other_info(line)
                for variable in variables:
                    if self.modifies_table.is_modified(variable, other_info['value']):
                        result.add(variable)
        elif param_first in self.statements:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_first))
            for line in lines_by_type_name:
                result.update(self.modifies_table.get_modified(str(line)))
        else:
            # procedura jak 1 parametr
            if param_first == 'PROCEDURE':
                proc_names: List[str] = self.proc_table.get_all_proc_name()
                variables: List[str] = self.var_table.table['variable_name'].tolist()
                for variable in variables:
                    for proc_name in proc_names:
                        if self.modifies_table.is_modified(variable, proc_name):
                            result.add(variable)
            else:
                # nazwa procedury
                variables: List[str] = self.var_table.table['variable_name'].tolist()
                for variable in variables:
                    if self.modifies_table.is_modified(variable, param_first):
                        result.add(variable)
        return list(result)

    def _digit_and_wild_card_or_variable(self, param_first) -> List[str]:
        result: List[str] = []
        variables: List[str] = self.var_table.table['variable_name'].tolist()
        for variable in variables:
            if self.modifies_table.is_modified(variable, param_first):
                result.append(variable)
        return result
