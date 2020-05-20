from typing import List, Union, Set, Tuple

from aitsi_parser.ParentTable import ParentTable
from aitsi_parser.StatementTable import StatementTable


class ParentRelation:
    statements = ['WHILE', 'IF', 'CALL', 'ASSIGN']

    def __init__(self, parent_table: ParentTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.parent_table: ParentTable = parent_table
        self.stmt_table: StatementTable = stmt_table

    def execute(self, param_first: str, param_second: str) -> Union[Tuple[bool, None],
                                                                    Tuple[List[int], None],
                                                                    Tuple[list, list]]:
        if param_first.isdigit():
            if param_second.isdigit():
                # p1 i p2 sa liczbami
                return self.parent_table.is_parent(int(param_first), int(param_second)), None
            elif param_second == '_':
                # p1 jest liczba, a p2  "_"
                return self.parent_table.get_child(int(param_first)), None
            else:
                # p1 jest liczba, a p2 str np. "CALL"
                return self._digit_and_string_with_type(param_first, param_second)
        elif param_first == '_':
            if param_second.isdigit():
                # p1  "_"  p2 jest liczba
                return self.parent_table.get_parent(int(param_second)), None
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

    def _two_wild_cards(self) -> Tuple[List, List]:
        return self.parent_table.table.index.tolist(), self.parent_table.table.columns.tolist()

    def _wild_card_and_str_with_type(self, param_second) -> Tuple[List[int], None]:
        lines_by_type_name: List[int] = []
        if param_second == 'STMT':
            lines_by_type_name = self.stmt_table.get_all_statement_lines()
        else:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_second))
        result = {line for line in lines_by_type_name if self.parent_table.get_parent(line)}
        return list(result), None

    def _two_str_with_types(self, param_first, param_second) -> Tuple[List[int], List[int]]:
        result_left = self._get_left_result_two_str_types(param_first, param_second)
        result_right = self._get_right_result_two_str_types(param_first, param_second)
        return list(result_left), list(result_right)

    def _get_right_result_two_str_types(self, param_first, param_second):
        children: Set[int] = set()
        lines_by_type_name_right: List[int] = []
        if param_first == 'STMT':
            lines_by_type_name_right = self.stmt_table.get_all_statement_lines()
        else:
            lines_by_type_name_right.extend(self.stmt_table.get_statement_line_by_type_name(param_first))
        for line in lines_by_type_name_right:
            children.update(self.parent_table.get_child(line))
        if param_second == 'STMT':
            result_right = {child for child in children}
        else:
            result_right = {child for child in children if
                            self.stmt_table.get_other_info(child)['name'] == param_second}
        return result_right

    def _get_left_result_two_str_types(self, param_first, param_second):
        parents: Set[int] = set()
        if param_second == 'STMT':
            lines_by_type_name_left = self.stmt_table.get_all_statement_lines()
        else:
            lines_by_type_name_left = self.stmt_table.get_statement_line_by_type_name(param_second)
        for line in lines_by_type_name_left:
            parents.update(self.parent_table.get_parent(line))
        if param_first == 'STMT':
            result_left = {parent for parent in parents}
        else:
            result_left = {parent for parent in parents if
                           self.stmt_table.get_other_info(parent)['name'] == param_first}
        return result_left

    def _str_with_type_and_wild_card(self, param_first) -> Tuple[List[int], None]:
        parents: Set[int] = set()
        lines_by_type_name: List[int] = self.stmt_table.get_all_statement_lines()
        for line in lines_by_type_name:
            parents.update(self.parent_table.get_parent(line))
        if param_first == 'STMT':
            result = {parent for parent in parents}
        else:
            result = {parent for parent in parents if self.stmt_table.get_other_info(parent)['name'] == param_first}
        return list(result), None

    def _str_with_type_and_digit(self, param_first, param_second) -> Tuple[List[int], None]:
        parents = self.parent_table.get_parent(int(param_second))
        if param_first == 'STMT':
            result = {parent for parent in parents}
        else:
            result = {parent for parent in parents if self.stmt_table.get_other_info(parent)['name'] == param_first}
        return list(result), None

    def _digit_and_string_with_type(self, param_first, param_second) -> Tuple[List[int], None]:
        children: List[int] = self.parent_table.get_child(int(param_first))
        if param_second == 'STMT':
            result = {child for child in children}
        else:
            result = {child for child in children if self.stmt_table.get_other_info(child)['name'] in param_second}
        return list(result), None
