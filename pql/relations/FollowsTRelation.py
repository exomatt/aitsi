from typing import Union, Tuple, List, Set

from aitsi_parser.FollowsTable import FollowsTable
from aitsi_parser.StatementTable import StatementTable


class FollowsTRelation:
    statements = ['WHILE', 'IF', 'CALL', 'ASSIGN']

    def __init__(self, follows_table: FollowsTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.stmt_table: StatementTable = stmt_table
        self.follows_table: FollowsTable = follows_table

    def execute(self, param_first: str, param_second: str) -> Union[Tuple[bool, bool],
                                                                    Tuple[List[int], List[str]],
                                                                    Tuple[List[str], None],
                                                                    Tuple[List[int], None],
                                                                    Tuple[bool, List[int]],
                                                                    Tuple[List[str], List[int]],
                                                                    Tuple[List[str], List[str]],
                                                                    Tuple[List[int], List[int]],
                                                                    Tuple[List[int], bool]]:

        if param_first.isdigit():
            if param_second.isdigit():
                # p1 i p2 sa liczbami
                return self._follows_T_two_digits(param_first, param_second)
            elif param_second == '_':
                # p1 jest liczba, a p2  "_"
                return self._follows_T_digit_and_wild_card(int(param_first))
            else:
                # p1 jest liczba, a p2 str np. "CALL"
                return self._follows_T_digit_str_type(param_first, param_second)
        elif param_first == '_':
            if param_second.isdigit():
                # p1  "_"  p2 jest liczba
                return self._follows_T_wild_card_and_digit(int(param_second))
            elif param_second == '_':
                # p1  "_", a p2  "_"
                return self.follows_table.table.index.tolist(), self.follows_table.table.columns.tolist()
            else:
                # p1  "_", a p2 str np. "CALL"
                return self._follows_T_wildcard_and_str_with_type(param_second)
        else:
            if param_second.isdigit():
                # p1 str np. "IF"  p2 jest liczba
                return self._follows_T_str_with_type_and_digit(param_first, param_second)
            elif param_second == '_':
                # p1 str np. "IF", a p2  "_"
                return self._follows_T_str_with_type_and_wildcard(param_first)
            else:
                # p1 str np. "IF", a p2 str np. "CALL"
                return self._follows_T_two_str_with_types(param_first, param_second)

    def get_all_lines_in_stmt_lst_before_line(self, line_number: int) -> List[int]:
        pom: Union[int, None] = self.follows_table.get_follows(int(line_number))
        results: List[int] = []
        while pom is not None:
            results.append(pom)
            pom = self.follows_table.get_follows(pom)
        return results

    def get_all_lines_in_stmt_lst_after_line(self, line_number: int) -> List[int]:
        pom: Union[int, None] = self.follows_table.get_child(int(line_number))
        results: List[int] = []
        while pom is not None:
            results.append(pom)
            pom = self.follows_table.get_child(pom)
        return results

    def _follows_T_two_digits(self, param_first, param_second) -> Tuple[bool, None]:
        pom: List[int] = self.get_all_lines_in_stmt_lst_after_line(int(param_first))
        if int(param_second) in pom:
            return True, None
        else:
            return False, None

    def _follows_T_digit_and_wild_card(self, param_first) -> Tuple[bool, None]:
        if self.get_all_lines_in_stmt_lst_after_line(int(param_first)):
            return True, None
        return False, None

    def _follows_T_wild_card_and_digit(self, param_second) -> Tuple[bool, None]:
        if self.get_all_lines_in_stmt_lst_before_line(int(param_second)):
            return True, None

    def _follows_T_digit_str_type(self, param_first, param_second) -> Tuple[List[int], None]:
        if param_second == 'STMT':
            pom: List[int] = self.follows_table.table.columns.tolist()
        else:
            pom: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
        return list(set(self.get_all_lines_in_stmt_lst_after_line(param_first)).intersection(pom)), None

    def _follows_T_wildcard_and_str_with_type(self, param_second) -> Tuple[List[int], None]:
        if param_second == 'STMT':
            pom: List[int] = self.follows_table.table.columns.tolist()
        else:
            pom: List[int] = list(set(self.stmt_table.get_statement_line_by_type_name(param_second)).intersection(
                self.follows_table.table.columns.tolist()))
        return pom, None

    def _follows_T_str_with_type_and_digit(self, param_first, param_second) -> Tuple[List[int], None]:
        if param_first == 'STMT':
            pom: List[int] = self.follows_table.table.index.tolist()
        else:
            pom: List[int] = self.stmt_table.get_statement_line_by_type_name(param_first)
        return list(set(self.get_all_lines_in_stmt_lst_before_line(param_second)).intersection(pom)), None

    def _follows_T_str_with_type_and_wildcard(self, param_first) -> Tuple[List[int], None]:
        if param_first == 'STMT':
            pom: List[int] = self.follows_table.table.index.tolist()
        else:
            pom: List[int] = list(set(self.stmt_table.get_statement_line_by_type_name(param_first)).intersection(
                self.follows_table.table.index.tolist()))
        return pom, None

    def _follows_T_two_str_with_types(self, param_first, param_second) -> Tuple[List[int], List[int]]:
        if param_first == 'STMT':
            if param_second == 'STMT':
                return self.follows_table.table.index.tolist(), self.follows_table.table.columns.tolist()
            else:
                pom_second: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
                result_first: Set[int] = set()
                result_second: List[int] = []
                for line in pom_second:
                    pom: List[int] = self.get_all_lines_in_stmt_lst_before_line(line)
                    if pom:
                        result_first.update(pom)
                        result_second.append(line)
                return list(result_first), result_second
        else:
            pom_first: List[int] = self.stmt_table.get_statement_line_by_type_name(param_first)
            if param_second == 'STMT':
                result_first: List[int] = []
                result_second: Set[int] = set()
                for line in pom_first:
                    pom: List[int] = self.get_all_lines_in_stmt_lst_after_line(line)
                    if pom:
                        result_first.append(line)
                        result_second.update(pom)
                return result_first, list(result_second)
            else:
                pom_second: List[int] = self.stmt_table.get_statement_line_by_type_name(param_second)
                result_first: List[int] = []
                result_second: Set[int] = set()
                for line in pom_first:
                    pom: List[int] = list(
                        set(self.get_all_lines_in_stmt_lst_after_line(line)).intersection(set(pom_second)))
                    if pom:
                        result_first.append(line)
                        result_second.update(pom)
                return result_first, list(result_second)
