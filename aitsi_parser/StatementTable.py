from typing import List, Union, Dict


class StatementTable:

    def __init__(self, table: Union[Dict, List]) -> None:
        self.table: Union[Dict, List] = table

    def get_other_info(self, statement_line: int) -> dict:
        return self.table[statement_line - 1]['other_info']

    def get_statement_line_by_type_name(self, type_name: str) -> List[int]:
        return [element['statement_line'] for element in self.table if element['other_info']['name'] == type_name]

    def get_statement_line_by_type_name_and_value(self, type_name: str, value: str) -> List[int]:
        return [element['statement_line'] for element in self.table if
                element['other_info']['name'] == type_name and element['other_info']['value'] == value]

    def get_all_statement_lines(self) -> List[int]:
        return list(range(1, len(self.table) + 1))

    def get_size(self) -> int:
        return len(self.table)

    def is_in(self, statement_line: int) -> bool:
        return len(self.table) >= statement_line > 0

    def to_string(self) -> None:
        print("StatementTable:")
        print(self.table)

    def to_log(self) -> str:
        return "StatementTable: \n" + str(self.table)
