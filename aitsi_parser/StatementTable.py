import json
from typing import List

import pandas as pd


class StatementTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame(columns=['statement_line', 'other_info'])
        else:
            for i in range(len(table.other_info)):
                json_data = table.other_info[i].replace("'", "\"")
                table.at[i, 'other_info'] = json.loads(json_data)
        self.table: pd.DataFrame = table

    def insert_statement(self, statement_line: int, other_info=None) -> int:
        if other_info is None:
            other_info = {}
        self.table = self.table.append({'statement_line': statement_line, 'other_info': other_info}, ignore_index=True)
        self.table = self.table.drop_duplicates('statement_line', ignore_index=True)
        return self.table.loc[self.table['statement_line'] == statement_line].index[0]

    def update_statement(self, statement_line: int, other_info: dict):
        self.table.loc[self.table['statement_line'] == statement_line]['other_info'][
            self.get_statement_index(statement_line)].update(other_info)

    def get_statement_line(self, index: int) -> int:
        return self.table.loc[index].statement_line

    def get_other_info(self, statement_line: int) -> dict:
        return self.table.loc[self.table['statement_line'] == statement_line].other_info[
            self.get_statement_index(statement_line)]

    def get_statement_index(self, statement_line: int) -> int:
        return self.table.loc[self.table['statement_line'] == statement_line].index[0]

    def get_statement_line_by_type_name(self, type_name: str) -> List[int]:
        return self.table.loc[self.table['other_info']
            .apply(lambda line: line['name'] == type_name)]['statement_line'].tolist()

    def get_statement_line_by_type_name_and_value(self, type_name: str, value: str) -> List[int]:
        return self.table.loc[self.table['other_info']
            .apply(lambda line: line['name'] == type_name & line['value'] == value)]['statement_line'].tolist()

    def get_all_statement_lines(self) -> List[int]:
        return self.table['statement_line'].tolist()

    def get_size(self) -> int:
        return len(self.table)

    def is_in(self, statement_line: int) -> bool:
        statements: pd.Series = self.table['statement_line'] == statement_line
        for statement in statements:
            if statement:
                return True
        return False

    def to_string(self) -> None:
        print("StatementTable:")
        print(self.table.to_string())

    def to_log(self) -> str:
        return "StatementTable: \n" + self.table.to_string()
