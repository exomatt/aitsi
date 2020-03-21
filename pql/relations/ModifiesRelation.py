from typing import Union, List, Set

from aitsi_parser.ModifiesTable import ModifiesTable
from aitsi_parser.VarTable import VarTable
from pql.Node import Node
from pql.utils.SearchUtils import SearchUtils


class ModifiesRelation:
    def __init__(self, ast_tree: Node, modifies_table: ModifiesTable, var_table: VarTable) -> None:
        super().__init__()
        self.ast_tree: Node = ast_tree
        self.modifies_table: ModifiesTable = modifies_table
        self.var_table: VarTable = var_table

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
                return self.modifies_table.is_modified(param_second, int(param_first))
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
                return self._str_type_and_wild_card(param_first)
            elif param_second == 'VARIABLE':
                # wedlug handbooka to kiedy jest if i while to zwracamy wszystkie modyfikowane  zmienne
                # np. 'VARIABLE' Modifies('IF',v)
                return self._str_type_and_wild_card(param_first)
            else:
                # p1 jest stmt np 'IF', a p2 zmienna variable np. 'x' zwracamy numer lini tego ifa
                return self._str_with_type_and_variable_by_name(param_first, param_second)

    def _str_with_type_and_variable_by_name(self, param_first, param_second):
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        result: List[int] = []
        lines_numbers: List[int] = []
        lines_numbers.extend(search_utils.find_node_line_number_by_type(param_first))
        for number in lines_numbers:
            if self.modifies_table.is_modified(param_second, number):
                result.append(number)
        return result

    def _str_type_and_wild_card(self, param_first):
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        result: Set[str] = set()
        lines_numbers: List[int] = []
        lines_numbers.extend(search_utils.find_node_line_number_by_type(param_first))
        for number in lines_numbers:
            result.update(self.modifies_table.get_modified(number))
        return list(result)

    def _digit_and_wild_card_or_variable(self, param_first):
        result: List[str] = []
        variables: List[str] = self.var_table.table['variable_name'].tolist()
        for variable in variables:
            if self.modifies_table.is_modified(variable, int(param_first)):
                result.append(variable)
        return result
