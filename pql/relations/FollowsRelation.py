from typing import List, Union, Tuple

from aitsi_parser import FollowsTable
from aitsi_parser.StatementTable import StatementTable


class FollowsRelation:
    statements = ['WHILE', 'IF', 'CALL', 'ASSIGN']

    def __init__(self, follows_table: FollowsTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.stmt_table: StatementTable = stmt_table
        self.follows_table: FollowsTable = follows_table

    def value_from_set_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        pass

    def value_from_set_and_not_initialized_set(self, param_first: str, param_second: str) -> List[str]:
        pass

    def value_from_set_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        pass

    def not_initialized_set_and_value_from_set(self, param_first: str, param_second: str) -> List[str]:
        pass

    def not_initialized_set_and_not_initialized_set(self, param_first: str, param_second: str) -> \
            Tuple[List[str], List[str]]:
        pass

    def not_initialized_set_and_value_from_query(self, param_first: str, param_second: str) -> List[str]:
        pass

    def value_from_query_and_value_from_set(self, param_first: str, param_second: str) -> bool:
        pass

    def value_from_query_and_not_initialized_set(self, param_first: str, param_second: str) -> List[str]:
        pass

    def value_from_query_and_value_from_query(self, param_first: str, param_second: str) -> bool:
        pass

    def execute(self, param_first: str, param_second: str) -> Union[Tuple[bool, None],
                                                                    Tuple[List[int], List[str]],
                                                                    Tuple[List[str], None],
                                                                    Tuple[List[int], None],
                                                                    Tuple[List[str], List[str]],
                                                                    Tuple[List[int], List[int]],
                                                                    Tuple[bool, List[int]],
                                                                    Tuple[List[int], bool]]:

        if param_first.isdigit():
            if param_second.isdigit():
                # p1 i p2 sa liczbami
                return self.follows_table.is_follows(int(param_first), int(param_second)), None
            elif param_second == '_':
                # p1 jest liczba, a p2  "_"
                return self._digit_and_wild_card(int(param_first))
            else:
                # p1 jest liczba, a p2 str np. "CALL"
                return self._digit_and_string_with_type(param_first, param_second)
        elif param_first == '_':
            if param_second.isdigit():
                # p1  "_"  p2 jest liczba
                return self._wild_card_and_digit(int(param_second))
            elif param_second == '_':
                # p1  "_", a p2  "_"
                return self.follows_table.table.index.tolist(), self.follows_table.table.columns.tolist()
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

    def _wild_card_and_str_with_type(self, param_second) -> Tuple[List[int], None]:
        if param_second == 'STMT':
            return self.follows_table.table.columns.tolist(), None
        else:
            lines_numbers: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
            return [line for line in lines_numbers if self.follows_table.get_follows(line) is not None], None

    def _digit_and_wild_card(self, param_first) -> Tuple[bool, None]:
        if self.follows_table.get_child(int(param_first)) is not None:
            return True, None
        return False, None

    def _wild_card_and_digit(self, param_second) -> Tuple[bool, None]:
        if self.follows_table.get_child(int(param_second)) is not None:
            return True, None
        return False, None

    def _two_str_with_types(self, param_first, param_second) -> Tuple[List[int], List[int]]:
        if param_first == 'STMT':
            if param_second == 'STMT':
                return self.follows_table.table.index.tolist(), self.follows_table.table.columns.tolist()
            else:
                param_second_lines: List[int] = list(
                    set(self.stmt_table.get_statement_line_by_type_name(param_second)).intersection(
                        set(self.follows_table.table.columns.tolist())))
                return list(filter(lambda line: line is not None, [self.follows_table.get_follows(line) for line in
                                                                   param_second_lines])), param_second_lines
        else:
            param_first_lines: List[int] = list(
                set(self.stmt_table.get_statement_line_by_type_name(param_first)).intersection(
                    set(self.follows_table.table.index.tolist())))
            if param_second == 'STMT':
                return param_first_lines, list(filter(lambda line: line is not None,
                                                      [self.follows_table.get_child(line) for line in
                                                       param_first_lines]))
            else:
                param_second_lines: List[int] = list(
                    set(self.stmt_table.get_statement_line_by_type_name(param_second)).intersection(
                        set(self.follows_table.columns.tolist())))
                return list(filter(lambda line: line is not None, [line for line in param_first_lines if
                                                                   self.follows_table.get_child(
                                                                       line) in param_second_lines])), \
                       list(filter(lambda line: line is not None, [line for line in param_second_lines if
                                                                   self.follows_table.get_follows(
                                                                       line) in param_first_lines]))

    def _str_with_type_and_wild_card(self, param_first) -> Tuple[List[int], None]:
        if param_first == 'STMT':
            return self.follows_table.table.index.tolist(), None
        else:
            return list(set(self.stmt_table.get_statement_line_by_type_name(param_first)).intersection(
                set(self.follows_table.table.index.tolist()))), None

    def _str_with_type_and_digit(self, param_first, param_second) -> Tuple[List[int], None]:
        follows_line: Union[int, None] = self.follows_table.get_follows(int(param_second))
        if follows_line is not None:
            if param_first == 'STMT' or follows_line in self.stmt_table.get_statement_line_by_type_name(param_first):
                return [follows_line], None
            else:
                return [], None
        else:
            return [], None

    def _digit_and_string_with_type(self, param_first, param_second) -> Tuple[List[int], None]:
        child_line: Union[int, None] = self.follows_table.get_child(int(param_first))
        if child_line is not None:
            if param_second == 'STMT' or child_line in self.stmt_table.get_statement_line_by_type_name(param_second):
                return [child_line], None
            else:
                return [], None
        else:
            return [], None


