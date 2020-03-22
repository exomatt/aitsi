from typing import Union, List, Set

from aitsi_parser.UsesTable import UsesTable
from aitsi_parser.VarTable import VarTable
from pql.Node import Node
from pql.utils.SearchUtils import SearchUtils


class UsesRelation:

    def __init__(self, ast_tree: Node, uses_table: UsesTable, var_table: VarTable) -> None:
        super().__init__()
        self.ast_tree: Node = ast_tree
        self.uses_table: UsesTable = uses_table
        self.var_table: VarTable = var_table

    def uses(self, param_first: str, param_second: str) -> Union[bool, List[str], List[int]]:
        if param_first.isdigit():
            if param_second == '_':
                # p1 - numer linii | p2 - '_'
                return self.uses_table.get_used(int(param_first))
            elif param_second == 'VARIABLE':
                # p1 - numer linii | p2 - zmienna jakaś
                return self.uses_table.get_used(int(param_first))
            else:
                # p1 - numer linii | p2 - zmienna konkretna (np. "x")
                return self.uses_table.is_used(param_second, int(param_first))
        elif param_first == '_':
            if param_second == '_':
                # p1 - '_' | p2 - '_'
                return self.uses_table.table.columns.values
            elif param_second == 'VARIABLE':
                # p1 - '_' | p2 - zmienna jakaś
                return self.uses_table.table.columns.values
            else:
                # p1 - '_' | p2 - zmienna konkretna (np. "x")
                return self.uses_table.get_uses(param_second)
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

    def _str_type_and_variable_name(self, param_first, param_second):
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        result: List[int] = []
        lines_numbers: List[int] = []
        lines_numbers.extend(search_utils.find_node_line_number_by_type(param_first))
        for number in lines_numbers:
            if self.uses_table.is_used(param_second, number):
                result.append(number)
        return result

    def _str_type_and_wildcard(self, param_first):
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        result: Set[str] = set()
        lines_numbers: List[int] = []
        lines_numbers.extend(search_utils.find_node_line_number_by_type(param_first))
        for number in lines_numbers:
            result.update(self.uses_table.get_used(number))
        return list(result)
