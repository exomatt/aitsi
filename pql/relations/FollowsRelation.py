from typing import List, Union

from aitsi_parser import FollowsTable
from pql.Node import Node
from pql.utils.SearchUtils import SearchUtils


class FollowsRelation:
    statements = ['WHILE', 'IF', 'CALL', 'ASSIGN']

    def __init__(self, ast_tree: Node, follows_table: FollowsTable) -> None:
        super().__init__()
        self.ast_tree: Node = ast_tree
        self.follows_table: FollowsTable = follows_table

    def follows(self, param_first: str, param_second: str) -> Union[bool, List[int]]:

        if param_first.isdigit():
            if param_second.isdigit():
                # p1 i p2 sa liczbami
                return self.follows_table.is_follows(int(param_first), int(param_second))
            elif param_second == '_':
                # p1 jest liczba, a p2  "_"
                return self.follows_table.get_child(int(param_first))
            else:
                # p1 jest liczba, a p2 str np. "CALL"
                return self._digit_and_string_with_type(param_first, param_second)
        elif param_first == '_':
            if param_second.isdigit():
                # p1  "_"  p2 jest liczba
                return self.follows_table.get_follows(int(param_second))
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

    def _two_wild_cards(self):
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        result: List[int] = []
        for number in range(search_utils.find_last_line_number()):
            result.extend(self.follows_table.get_child(number))
        return result

    def _wild_card_and_str_with_type(self, param_second):
        result: List[int] = []
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        lines_numbers: List[int] = search_utils.find_node_line_number_by_type(param_second)
        for number in lines_numbers:
            parents: List[int] = self.follows_table.get_follows(number)
            if len(parents) != 0:
                result.append(number)
        return result

    def _two_str_with_types(self, param_first, param_second):
        result: List[int] = []
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        p1_lines_numbers: List[int] = []
        p1_lines_numbers.extend(search_utils.find_node_line_number_by_type(param_first))
        p2_lines_numbers: List[int] = []
        p2_lines_numbers.extend(search_utils.find_node_line_number_by_type(param_second))
        for p1_number in p1_lines_numbers:
            for p2_number in p2_lines_numbers:
                if self.follows_table.is_follows(p1_number, p2_number):
                    result.append(p2_number)
        return result

    def _str_with_type_and_wild_card(self, param_first):
        result: List[int] = []
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        lines_numbers: List[int] = []
        lines_numbers.extend(search_utils.find_node_line_number_by_type(param_first))
        for number in lines_numbers:
            result.extend(self.follows_table.get_child(number))
        return result

    def _str_with_type_and_digit(self, param_first, param_second):
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        lines_numbers: List[int] = []
        if param_first == 'STMT':
            for stmt in self.statements:
                lines_numbers.extend(search_utils.find_node_line_number_by_type(stmt))
        else:
            lines_numbers.extend(search_utils.find_node_line_number_by_type(param_first))
        lines_numbers.extend(search_utils.find_node_line_number_by_type(param_first))
        for number in lines_numbers:
            if self.follows_table.is_follows(number, int(param_second)):
                return [number]
        return []

    def _digit_and_string_with_type(self, param_first, param_second):
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        lines_numbers: List[int] = search_utils.find_node_line_number_by_type(param_second)
        for number in lines_numbers:
            if self.follows_table.is_follows(int(param_first), number):
                return True
        return False