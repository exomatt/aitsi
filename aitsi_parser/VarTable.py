import json

import pandas as pd


class VarTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame(columns=['variable_name', 'other_info'])
        else:
            for i in range(len(table.other_info)):
                json_data = table.other_info[i].replace("'", "\"")
                table.other_info[i] = json.loads(json_data)
        self.table: pd.DataFrame = table

    def insert_var(self, var_name: str) -> int:
        self.table = self.table.append({'variable_name': var_name, 'other_info': {}}, ignore_index=True)
        self.table = self.table.drop_duplicates('variable_name', ignore_index=True)
        return self.table.loc[self.table['variable_name'] == var_name].index[0]

    def get_var_name(self, index: int) -> str:
        return self.table.loc[index].variable_name

    def get_other_info(self, var_name: str) -> dict:
        return self.table.loc[self.table['variable_name'] == var_name].other_info[0]

    def get_var_index(self, var_name: str) -> int:
        return self.table.loc[self.table['variable_name'] == var_name].index[0]

    def get_size(self) -> int:
        return len(self.table)

    def is_in(self, var_name: str) -> bool:
        names: pd.Series = self.table['variable_name'] == var_name
        for name in names:
            if name:
                return True
        return False

    def to_string(self) -> None:
        print("VarTable:")
        print(self.table.to_string())
