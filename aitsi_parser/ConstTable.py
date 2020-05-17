import json
from typing import List

import pandas as pd


class ConstTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame(columns=['constant', 'other_info'])
        else:
            for i in range(len(table.other_info)):
                json_data = table.other_info[i].replace("'", "\"")
                table.at[i, 'other_info'] = json.loads(json_data)
        self.table: pd.DataFrame = table

    def insert_const(self, constant: int) -> int:
        self.table = self.table.append({'constant': constant, 'other_info': {}}, ignore_index=True)
        self.table = self.table.drop_duplicates('constant', ignore_index=True)
        return self.table.loc[self.table['constant'] == constant].index[0]

    def update_const(self, constant: int, other_info: dict):
        self.table.loc[self.table['constant'] == constant]['other_info'][
            self.get_constant_index(constant)].update(other_info)

    def get_constant(self, index: int) -> int:
        return self.table.loc[index].constant

    def get_all_constant(self) -> List[str]:
        return self.table['constant'].tolist()

    def get_other_info(self, constant: int) -> dict:
        return self.table.loc[self.table['constant'] == constant].other_info[self.get_constant_index(constant)]

    def get_constant_index(self, constant: int) -> int:
        return self.table.loc[self.table['constant'] == constant].index[0]

    def get_size(self) -> int:
        return len(self.table)

    def is_in(self, constant: int) -> bool:
        values: pd.Series = self.table['constant'] == constant
        for value in values:
            if value:
                return True
        return False

    def to_string(self) -> None:
        print("ConstTable:")
        print(self.table.to_string())

    def to_log(self) -> str:
        return "ConstTable: \n" + self.table.to_string()
