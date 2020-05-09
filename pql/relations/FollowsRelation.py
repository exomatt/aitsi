from typing import List, Union, Tuple

from aitsi_parser import FollowsTable
from aitsi_parser.StatementTable import StatementTable


class FollowsRelation:
    statements = ['WHILE', 'IF', 'CALL', 'ASSIGN']

    def __init__(self, follows_table: FollowsTable, stmt_table: StatementTable) -> None:
        super().__init__()
        self.stmt_table: StatementTable = stmt_table
        self.follows_table: FollowsTable = follows_table

    def follows(self, param_first: str, param_second: str) -> Union[Tuple[bool, None],
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

    def _two_wild_cards(self) -> Tuple[List[int], List[int]]:
        result: List[int] = []
        for number in range(self.stmt_table.get_size()):
            result.extend(self.follows_table.get_child(number))
        return result, result

    def _wild_card_and_str_with_type(self, param_second) -> Tuple[List[int], List[int]]:
        result: List[int] = []
        result_second: List[int] = []
        lines_numbers: List[int] = []
        if param_second == 'STMT':
            for stmt in self.statements:
                lines_numbers.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_numbers = self.stmt_table.get_statement_line_by_type_name(param_second)
        for number in lines_numbers:
            parents: List[int] = self.follows_table.get_follows(number)
            if len(parents) != 0:
                result.append(number)
                result_second.append(parents[0])
        return result, result_second

    def _digit_and_wild_card(self, param_first) -> Tuple[bool, List[int]]:
        result: List[int] = self.follows_table.get_child(int(param_first))
        is_follows: bool = False
        if len(result) > 0:
            is_follows = True
        return is_follows, result

    def _wild_card_and_digit(self, param_second) -> Tuple[List[int], bool]:
        result: List[int] = self.follows_table.get_follows(int(param_second))
        is_follows: bool = False
        if len(result) > 0:
            is_follows = True
        return result, is_follows

    def _two_str_with_types(self, param_first, param_second) -> Tuple[List[int], List[int]]:
        result_param_second: List[int] = []
        result_param_first: List[int] = []
        p1_lines_numbers: List[int] = []
        p2_lines_numbers: List[int] = []
        if param_first == 'STMT':
            for stmt in self.statements:
                p1_lines_numbers.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            p1_lines_numbers = self.stmt_table.get_statement_line_by_type_name(param_first)
        if param_second == 'STMT':
            for stmt in self.statements:
                p2_lines_numbers.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            p2_lines_numbers = self.stmt_table.get_statement_line_by_type_name(param_second)
        for p1_number in p1_lines_numbers:
            for p2_number in p2_lines_numbers:
                if self.follows_table.is_follows(p1_number, p2_number):
                    result_param_second.append(p2_number)
                    result_param_first.append(p1_number)
        return result_param_first, result_param_second

    def _str_with_type_and_wild_card(self, param_first) -> Tuple[List[int], List[int]]:
        result: List[int] = []
        result_second: List[int] = []
        lines_numbers: List[int] = []
        if param_first == 'STMT':
            for stmt in self.statements:
                lines_numbers.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_numbers = self.stmt_table.get_statement_line_by_type_name(param_first)
        for number in lines_numbers:
            result_second.extend(self.follows_table.get_child(number))
            if len(self.follows_table.get_child(number)) != 0:
                result.append(number)
        return result, result_second

    def _str_with_type_and_digit(self, param_first, param_second) -> Tuple[List[int], None]:
        lines_numbers: List[int] = []
        if param_first == 'STMT':
            for stmt in self.statements:
                lines_numbers.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_numbers.extend(self.stmt_table.get_statement_line_by_type_name(param_first))
        lines_numbers.extend(self.stmt_table.get_statement_line_by_type_name(param_first))
        for number in lines_numbers:
            if self.follows_table.is_follows(number, int(param_second)):
                return [number], None
        return [], None

    def _digit_and_string_with_type(self, param_first, param_second) -> Tuple[List[int], None]:
        lines_numbers: List[int] = []
        if param_second == 'STMT':
            for stmt in self.statements:
                lines_numbers.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            lines_numbers = self.stmt_table.get_statement_line_by_type_name(param_second)
        for number in lines_numbers:
            if self.follows_table.is_follows(int(param_first), number):
                return [number], None
        return [], None

    def follows_T(self, param_first: str, param_second: str) -> Union[Tuple[bool, bool],
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
                return self._follows_T_two_wildcards()
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

    def get_all_lines_in_stmt_lst_after_line(self, line_number: int) -> List[int]:
        pom: List[int] = self.follows_table.get_child(int(line_number))
        results: List[int] = []
        while pom:
            results.append(pom[0])
            pom = self.follows_table.get_child(pom[0])
        return results

    def get_all_lines_in_stmt_lst_before_line(self, line_number: int) -> List[int]:
        pom: List[int] = self.follows_table.get_follows(int(line_number))
        results: List[int] = []
        while pom:
            results.append(pom[0])
            pom = self.follows_table.get_follows(pom[0])
        return results

    def _follows_T_two_digits(self, param_first, param_second) -> Tuple[bool, bool]:
        pom: List[int] = self.get_all_lines_in_stmt_lst_after_line(int(param_first))
        if int(param_second) in pom:
            return True, True
        else:
            return False, False

    def _follows_T_digit_and_wild_card(self, param_first) -> Tuple[bool, List[int]]:
        result: List[int] = self.get_all_lines_in_stmt_lst_after_line(int(param_first))
        is_follows: bool = False
        if len(result) > 0:
            is_follows = True
        return is_follows, result

    def _follows_T_wild_card_and_digit(self, param_second) -> Tuple[List[int], bool]:
        result: List[int] = self.get_all_lines_in_stmt_lst_before_line(int(param_second))
        is_follows: bool = False
        if len(result) > 0:
            is_follows = True
        return result, is_follows

    def _follows_T_digit_str_type(self, param_first, param_second) -> Tuple[List[int], None]:
        pom: List[int] = []
        if param_second == 'STMT':
            for stmt in self.statements:
                pom.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            pom = self.stmt_table.get_statement_line_by_type_name(param_second)
        return list(set(self.get_all_lines_in_stmt_lst_after_line(param_first)).intersection(pom)), None

    def _follows_T_two_wildcards(self) -> Tuple[List[int], List[int]]:
        result: List[int] = [line for line in range(self.stmt_table.get_size())]
        return result, result

    def _follows_T_wildcard_and_str_with_type(self, param_second) -> Tuple[List[int], None]:
        pom: List[int] = []
        if param_second == 'STMT':
            for stmt in self.statements:
                pom.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            pom = self.stmt_table.get_statement_line_by_type_name(param_second)
        return list(set(pom)), None

    def _follows_T_str_with_type_and_digit(self, param_first, param_second) -> Tuple[List[int], None]:
        pom: List[int] = []
        if param_first == 'STMT':
            for stmt in self.statements:
                pom.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            pom = self.stmt_table.get_statement_line_by_type_name(param_first)
        return list(set(self.get_all_lines_in_stmt_lst_before_line(param_second)).intersection(pom)), None

    def _follows_T_str_with_type_and_wildcard(self, param_first) -> Tuple[List[int], List[int]]:
        pom: List[int] = []
        if param_first == 'STMT':
            for stmt in self.statements:
                pom.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            pom = self.stmt_table.get_statement_line_by_type_name(param_first)
        results: List[int] = []
        for i in pom:
            if self.get_all_lines_in_stmt_lst_after_line(i):
                results.append(i)
        return list(set(results)), self.stmt_table.get_statement_line_by_type_name(param_first)

    def _follows_T_two_str_with_types(self, param_first, param_second) -> Tuple[List[int], List[int]]:
        pom_first: List[int] = []
        if param_first == 'STMT':
            for stmt in self.statements:
                pom_first.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            pom_first = self.stmt_table.get_statement_line_by_type_name(param_first)
        pom_second: List[int] = []
        if param_second == 'STMT':
            for stmt in self.statements:
                pom_second.extend(self.stmt_table.get_statement_line_by_type_name(stmt))
        else:
            pom_second = self.stmt_table.get_statement_line_by_type_name(param_second)
        results_second: List[int] = []
        results_first: List[int] = []
        for i in pom_first:
            for j in self.get_all_lines_in_stmt_lst_after_line(i):
                if j in pom_second:
                    results_first.append(i)
        for k in pom_second:
            for m in self.get_all_lines_in_stmt_lst_before_line(k):
                if m in pom_first:
                    results_second.append(k)
        return list(set(results_first)), list(set(results_second))
