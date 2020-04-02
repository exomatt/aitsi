from typing import List, Union, Set, Tuple

from aitsi_parser.ParentTable import ParentTable
from aitsi_parser.StatementTable import StatementTable


class ParentRelation:
    statements = ['WHILE', 'IF', 'CALL', 'ASSIGN']

    def __init__(self, parent_table: ParentTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.parent_table: ParentTable = parent_table
        self.stmt_table: StatementTable = stmt_table

    def parent(self, param_first: str, param_second: str) -> Union[Tuple[bool, None],
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
        result: Set[int] = set()
        parents: List[int] = []
        lines_by_type_name: List[int] = []
        if param_second == 'STMT':
            for stmt in self.statements:
                lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_second))
        for line in lines_by_type_name:
            parents.extend(self.parent_table.get_parent(line))
        for parent in parents:
            if self.stmt_table.get_other_info(parent)['name'] in self.statements:
                result.add(parent)
        return list(result), None

    def _two_str_with_types(self, param_first, param_second) -> Tuple[List[int], List[int]]:
        result_left = self._get_left_result_two_str_types(param_first, param_second)
        result_right = self._get_right_result_two_str_types(param_first, param_second)
        return list(result_left), list(result_right)

    def _get_right_result_two_str_types(self, param_first, param_second):
        result_right: Set[int] = set()
        children: List[int] = []
        lines_by_type_name_right: List[int] = []
        if param_first == 'STMT':
            for stmt in self.statements:
                lines_by_type_name_right.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_by_type_name_right.extend(self.stmt_table.get_statement_line_by_type_name(param_first))
        for line in lines_by_type_name_right:
            children.extend(self.parent_table.get_child(line))
        if param_second == 'STMT':
            for child in children:
                if self.stmt_table.get_other_info(child)['name'] in self.statements:
                    result_right.add(child)
        else:
            for child in children:
                if self.stmt_table.get_other_info(child)['name'] == param_second:
                    result_right.add(child)
        return result_right

    def _get_left_result_two_str_types(self, param_first, param_second):
        result_left: Set[int] = set()
        parents: List[int] = []
        lines_by_type_name_left: List[int] = []
        if param_second == 'STMT':
            for stmt in self.statements:
                lines_by_type_name_left.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_by_type_name_left.extend(self.stmt_table.get_statement_line_by_type_name(param_second))
        for line in lines_by_type_name_left:
            parents.extend(self.parent_table.get_parent(line))
        if param_first == 'STMT':
            for parent in parents:
                if self.stmt_table.get_other_info(parent)['name'] in self.statements:
                    result_left.add(parent)
        else:
            for parent in parents:
                if self.stmt_table.get_other_info(parent)['name'] == param_first:
                    result_left.add(parent)
        return result_left

    def _str_with_type_and_wild_card(self, param_first) -> Tuple[List[int], None]:
        result: Set[int] = set()
        parents: List[int] = []
        lines_by_type_name: List[int] = []
        for stmt in self.statements:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        for line in lines_by_type_name:
            parents.extend(self.parent_table.get_parent(line))
        if param_first == 'STMT':
            for parent in parents:
                if self.stmt_table.get_other_info(parent)['name'] in self.statements:
                    result.add(parent)
        else:
            for parent in parents:
                if self.stmt_table.get_other_info(parent)['name'] == param_first:
                    result.add(parent)
        return list(result), None

    def _str_with_type_and_digit(self, param_first, param_second) -> Tuple[List[int], None]:
        result: Set[int] = set()
        parents = self.parent_table.get_parent(int(param_second))
        if param_first == 'STMT':
            for parent in parents:
                if self.stmt_table.get_other_info(parent)['name'] in self.statements:
                    result.add(parent)
        else:
            for parent in parents:
                if self.stmt_table.get_other_info(parent)['name'] == param_first:
                    result.add(parent)
        return list(result), None

    def _digit_and_string_with_type(self, param_first, param_second) -> Tuple[List[int], None]:
        result: Set[int] = set()
        children: List[int] = self.parent_table.get_child(int(param_first))
        if param_second == 'STMT':
            for child in children:
                if self.stmt_table.get_other_info(child)['name'] in self.statements:
                    result.add(child)
            return list(result), None
        else:
            for child in children:
                if self.stmt_table.get_other_info(child)['name'] in param_second:
                    result.add(child)
            return list(result), None

    def parent_T(self, param_first: str, param_second: str) -> Union[Tuple[bool, None],
                                                                     Tuple[List[int], None],
                                                                     Tuple[list, list]]:
        if param_first.isdigit():
            if param_second.isdigit():
                # p1 i p2 sa liczbami
                return self._parent_T_two_digits(param_first, param_second)
            elif param_second == '_':
                # p1 jest liczba, a p2  "_"
                return self._parent_T_digit_wildcard(param_first)
            else:
                # p1 jest liczba, a p2 str np. "CALL"
                return self._parent_T_digit_str_type(param_first, param_second)
        elif param_first == '_':
            if param_second.isdigit():
                # p1  "_"  p2 jest liczba
                return self._parent_T_wildcard_digit(param_second)
            elif param_second == '_':
                # p1  "_", a p2  "_"
                return self._two_wild_cards()
            else:
                # p1  "_", a p2 str np. "CALL"
                return self._parent_T_wildcard_str_type(param_second)
        else:
            if param_second.isdigit():
                # p1 str np. "IF"  p2 jest liczba
                return self._parent_T_str_type_digit(param_first, param_second)

            elif param_second == '_':
                # p1 str np. "IF", a p2  "_"
                return self._parent_T_str_type_wild_card(param_first)
            else:
                # p1 str np. "IF", a p2 str np. "CALL"
                return self._parent_T_two_str_types(param_first, param_second)

    def _parent_T_two_str_types(self, param_first, param_second) -> Tuple[List[int], List[int]]:
        result_left = self._result_left_parent_T_two_str(param_first, param_second)
        result_right = self._result_right_parent_T_two_str(param_first, param_second)
        return list(result_left), list(result_right)

    def _result_left_parent_T_two_str(self, param_first, param_second):
        result_left: Set[int] = set()
        parents: List[int] = []
        lines_by_type_name: List[int] = []
        if param_second == 'STMT':
            for stmt in self.statements:
                lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_second))
        for line in lines_by_type_name:
            parents.extend(self.parent_table.get_parent(line))
        if param_first == 'STMT':
            for parent in parents:
                parents.extend(self.parent_table.get_parent(parent))
                if self.stmt_table.get_other_info(parent)['name'] in self.statements:
                    result_left.add(parent)
        else:
            for parent in parents:
                parents.extend(self.parent_table.get_parent(parent))
                if self.stmt_table.get_other_info(parent)['name'] == param_first:
                    result_left.add(parent)
        return result_left

    def _result_right_parent_T_two_str(self, param_first, param_second):
        result_right: Set[int] = set()
        children: List[int] = []
        lines_by_type_name: List[int] = []
        if param_first == 'STMT':
            for stmt in self.statements:
                lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_first))
        for line in lines_by_type_name:
            children.extend(self.parent_table.get_child(line))
        if param_second == 'STMT':
            for child in children:
                children.extend(self.parent_table.get_child(child))
                if self.stmt_table.get_other_info(child)['name'] in self.statements:
                    result_right.add(child)
        else:
            for child in children:
                children.extend(self.parent_table.get_child(child))
                if self.stmt_table.get_other_info(child)['name'] == param_second:
                    result_right.add(child)
        return result_right

    def _parent_T_str_type_wild_card(self, param_first) -> Tuple[List[int], None]:
        result: Set[int] = set()
        parents: List[int] = []
        lines_by_type_name: List[int] = []
        for stmt in self.statements:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        for line in lines_by_type_name:
            parents.extend(self.parent_table.get_parent(line))
        if param_first == 'STMT':
            for parent in parents:
                parents.extend(self.parent_table.get_parent(parent))
                if self.stmt_table.get_other_info(parent)['name'] in self.statements:
                    result.add(parent)
        else:
            for parent in parents:
                parents.extend(self.parent_table.get_parent(parent))
                if self.stmt_table.get_other_info(parent)['name'] == param_first:
                    result.add(parent)
        return list(result), None

    def _parent_T_str_type_digit(self, param_first, param_second) -> Tuple[List[int], None]:
        result: Set[int] = set()
        parents = self.parent_table.get_parent(int(param_second))
        if param_first == 'STMT':
            for parent in parents:
                parents.extend(self.parent_table.get_parent(parent))
                if self.stmt_table.get_other_info(parent)['name'] in self.statements:
                    result.add(parent)
        else:
            for parent in parents:
                parents.extend(self.parent_table.get_parent(parent))
                if self.stmt_table.get_other_info(parent)['name'] == param_first:
                    result.add(parent)
        return list(result), None

    def _parent_T_wildcard_str_type(self, param_second) -> Tuple[List[int], None]:
        result: Set[int] = set()
        parents: List[int] = []
        lines_by_type_name: List[int] = []
        if param_second == 'STMT':
            for stmt in self.statements:
                lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(param_second))
        for line in lines_by_type_name:
            parents.extend(self.parent_table.get_parent(line))
        for parent in parents:
            parents.extend(self.parent_table.get_parent(parent))
            if self.stmt_table.get_other_info(parent)['name'] in self.statements:
                result.add(parent)
        return list(result), None

    def _parent_T_wildcard_digit(self, param_second) -> Tuple[List[int], None]:
        parents = self.parent_table.get_parent(int(param_second))
        for parent in parents:
            parents.extend(self.parent_table.get_parent(parent))
        return parents, None

    def _parent_T_digit_str_type(self, param_first, param_second) -> Tuple[List[int], None]:
        result: Set[int] = set()
        children: List[int] = self.parent_table.get_child(int(param_first))
        if param_second == 'STMT':
            for child in children:
                children.extend(self.parent_table.get_child(child))
                if self.stmt_table.get_other_info(child)['name'] in self.statements:
                    result.add(child)
            return list(result), None
        else:
            for child in children:
                children.extend(self.parent_table.get_child(child))
                if self.stmt_table.get_other_info(child)['name'] in param_second:
                    result.add(child)
            return list(result), None

    def _parent_T_digit_wildcard(self, param_first) -> Tuple[List[int], None]:
        children: List[int] = self.parent_table.get_child(int(param_first))
        for child in children:
            children.extend(self.parent_table.get_child(child))
        return children, None

    def _parent_T_two_digits(self, param_first, param_second) -> Tuple[bool, None]:
        is_parent = self.parent_table.is_parent(int(param_first), int(param_second))
        if is_parent:
            return is_parent, None
        else:
            children: List[int] = self.parent_table.get_child(int(param_first))
            for child in children:
                if int(param_second) in self.parent_table.get_child(child):
                    return True, None
                children.extend(self.parent_table.get_child(child))
            return False, None
