from typing import List, Union, Set

from aitsi_parser.ParentTable import ParentTable
from aitsi_parser.StatementTable import StatementTable


class ParentRelation:
    statements = ['WHILE', 'IF', 'CALL', 'ASSIGN']

    def __init__(self, parent_table: ParentTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.parent_table: ParentTable = parent_table
        self.stmt_table: StatementTable = stmt_table

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

    def _two_wild_cards(self) -> List[int]:
        result: Set[int] = set()
        parents: List[int] = []
        lines_by_type_name: List[int] = []
        for stmt in self.statements:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        for line in lines_by_type_name:
            parents.extend(self.parent_table.get_parent(line))
        for parent in parents:
            if self.stmt_table.get_other_info(parent)['name'] in self.statements:
                result.add(parent)
        return list(result)

    def _wild_card_and_str_with_type(self, param_second) -> List[int]:
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
        return list(result)

    def _two_str_with_types(self, param_first, param_second) -> List[int]:
        result: List[int] = []
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
                if self.stmt_table.get_other_info(parent)['name'] in self.statements:
                    result.append(parent)
        else:
            for parent in parents:
                if self.stmt_table.get_other_info(parent)['name'] == param_first:
                    result.append(parent)
        return result

    def _str_with_type_and_wild_card(self, param_first) -> List[int]:
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
        return list(result)

    def _str_with_type_and_digit(self, param_first, param_second) -> List[int]:
        result: List[int] = []
        parents = self.parent_table.get_parent(int(param_second))
        if param_first == 'STMT':
            for parent in parents:
                if self.stmt_table.get_other_info(parent)['name'] in self.statements:
                    result.append(parent)
        else:
            for parent in parents:
                if self.stmt_table.get_other_info(parent)['name'] == param_first:
                    result.append(parent)
        return result

    def _digit_and_string_with_type(self, param_first, param_second) -> List[int]:
        result: List[int] = []
        children: List[int] = self.parent_table.get_child(int(param_first))
        if param_second == 'STMT':
            for child in children:
                if self.stmt_table.get_other_info(child)['name'] in self.statements:
                    result.append(child)
            return result
        else:
            for child in children:
                if self.stmt_table.get_other_info(child)['name'] in param_second:
                    result.append(child)
            return result
        return result

    def parent_T(self, param_first: str, param_second: str) -> Union[bool, List[int]]:
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
                return self._parent_T_two_wildcard()
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

    def _parent_T_two_str_types(self, param_first, param_second) -> List[int]:
        result: List[int] = []
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
                    result.append(parent)
        else:
            for parent in parents:
                parents.extend(self.parent_table.get_parent(parent))
                if self.stmt_table.get_other_info(parent)['name'] == param_first:
                    result.append(parent)
        return result

    def _parent_T_str_type_wild_card(self, param_first) -> List[int]:
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
        return list(result)

    def _parent_T_str_type_digit(self, param_first, param_second) -> List[int]:
        result: List[int] = []
        parents = self.parent_table.get_parent(int(param_second))
        if param_first == 'STMT':
            for parent in parents:
                parents.extend(self.parent_table.get_parent(parent))
                if self.stmt_table.get_other_info(parent)['name'] in self.statements:
                    result.append(parent)
        else:
            for parent in parents:
                parents.extend(self.parent_table.get_parent(parent))
                if self.stmt_table.get_other_info(parent)['name'] == param_first:
                    result.append(parent)
        return result

    def _parent_T_wildcard_str_type(self, param_second) -> List[int]:
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
        return list(result)

    def _parent_T_two_wildcard(self) -> List[int]:
        result: Set[int] = set()
        parents: List[int] = []
        lines_by_type_name: List[int] = []
        for stmt in self.statements:
            lines_by_type_name.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        for line in lines_by_type_name:
            parents.extend(self.parent_table.get_parent(line))
        for parent in parents:
            parents.extend(self.parent_table.get_parent(parent))
            if self.stmt_table.get_other_info(parent)['name'] in self.statements:
                result.add(parent)
        return list(result)

    def _parent_T_wildcard_digit(self, param_second) -> List[int]:
        parents = self.parent_table.get_parent(int(param_second))
        for parent in parents:
            parents.extend(self.parent_table.get_parent(parent))
        return parents

    def _parent_T_digit_str_type(self, param_first, param_second) -> List[int]:
        result: List[int] = []
        children: List[int] = self.parent_table.get_child(int(param_first))
        if param_second == 'STMT':
            for child in children:
                children.extend(self.parent_table.get_child(child))
                if self.stmt_table.get_other_info(child)['name'] in self.statements:
                    result.append(child)
            return result
        else:
            for child in children:
                children.extend(self.parent_table.get_child(child))
                if self.stmt_table.get_other_info(child)['name'] in param_second:
                    result.append(child)
            return result

    def _parent_T_digit_wildcard(self, param_first) -> List[int]:
        children: List[int] = self.parent_table.get_child(int(param_first))
        for child in children:
            children.extend(self.parent_table.get_child(child))
        return children

    def _parent_T_two_digits(self, param_first, param_second) -> bool:
        is_parent = self.parent_table.is_parent(int(param_first), int(param_second))
        if is_parent:
            return is_parent
        else:
            children: List[int] = self.parent_table.get_child(int(param_first))
            for child in children:
                if int(param_second) in self.parent_table.get_child(child):
                    return True
                children.extend(self.parent_table.get_child(child))
            return False
