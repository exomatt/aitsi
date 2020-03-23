from typing import List, Union

from aitsi_parser.ParentTable import ParentTable
from pql.Node import Node
from pql.utils.SearchUtils import SearchUtils


class ParentRelation:
    statements = ['WHILE', 'IF', 'CALL', 'ASSIGN']

    def __init__(self, ast_tree: Node, parent_table: ParentTable) -> None:
        super().__init__()
        self.ast_tree: Node = ast_tree
        self.parent_table: ParentTable = parent_table

    def parent(self, param_first: str, param_second: str) -> Union[bool, List[int]]:

        if param_first.isdigit():
            if param_second.isdigit():
                # p1 i p2 sa liczbami
                return self.parent_table.is_parent(int(param_first), int(param_second))
            elif param_second == '_':
                # p1 jest liczba, a p2  "_"
                return self.parent_table.get_child(int(param_first))
            else:
                # p1 jest liczba, a p2 str np. "CALL"
                return self._digit_and_string_with_type(param_first, param_second)
        elif param_first == '_':
            if param_second.isdigit():
                # p1  "_"  p2 jest liczba
                return self.parent_table.get_parent(int(param_second))

                pass
            elif param_second == '_':
                # p1  "_", a p2  "_"
                return self._two_wild_cards()
            else:
                # p1  "_", a p2 str np. "CALL"
                return self._wild_card_and_str_with_type(param_second)
        else:
            if param_second.isdigit():
                # p1 str np. "IF"  p2 jest liczba
                return self._str_with_type_and_digit(param_first, param_second)
            elif param_second == '_':
                # p1 str np. "IF", a p2  "_"
                return self._str_with_type_and_wild_card(param_first)
            else:
                # p1 str np. "IF", a p2 str np. "CALL"
                return self._two_str_with_types(param_first, param_second)
        pass

    def _two_wild_cards(self):
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        result: List[int] = []
        lines_numbers: List[int] = []
        lines_numbers.extend(search_utils.find_node_line_number_by_type('WHILE'))
        lines_numbers.extend(search_utils.find_node_line_number_by_type('IF'))
        for number in lines_numbers:
            result.extend(self.parent_table.get_child(number))
        return result

    def _wild_card_and_str_with_type(self, param_second):
        result: List[int] = []
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        lines_numbers: List[int] = search_utils.find_node_line_number_by_type(param_second)
        for number in lines_numbers:
            parents: List[int] = self.parent_table.get_parent(number)
            if len(parents) != 0:
                result.append(number)
        return result

    def _two_str_with_types(self, param_first, param_second):
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        p1_lines_numbers: List[int] = []
        p1_lines_numbers.extend(search_utils.find_node_line_number_by_type(param_first))
        p2_lines_numbers: List[int] = []
        p2_lines_numbers.extend(search_utils.find_node_line_number_by_type(param_second))
        for p1_number in p1_lines_numbers:
            for p2_number in p2_lines_numbers:
                if self.parent_table.is_parent(p1_number, p2_number):
                    return [p2_number]
        return []

    def _str_with_type_and_wild_card(self, param_first):
        result: List[int] = []
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        lines_numbers: List[int] = []
        lines_numbers.extend(search_utils.find_node_line_number_by_type(param_first))
        for number in lines_numbers:
            result.extend(self.parent_table.get_child(number))
        return result

    def _str_with_type_and_digit(self, param_first, param_second):
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        lines_numbers: List[int] = []
        if param_first == 'STMT':
            for stmt in self.statements:
                lines_numbers.extend(search_utils.find_node_line_number_by_type(stmt))
        else:
            lines_numbers.extend(search_utils.find_node_line_number_by_type(param_first))
        for number in lines_numbers:
            if self.parent_table.is_parent(number, int(param_second)):
                return [number]
        return []

    def _digit_and_string_with_type(self, param_first, param_second):
        result: List[int] = []
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        lines_numbers: List[int] = []
        if param_second == 'STMT':
            for stmt in self.statements:
                lines_numbers.extend(search_utils.find_node_line_number_by_type(stmt))
        else:
            lines_numbers.extend(search_utils.find_node_line_number_by_type(param_second))
        for number in lines_numbers:
            if self.parent_table.is_parent(int(param_first), number):
                result.append(number)
        return result
