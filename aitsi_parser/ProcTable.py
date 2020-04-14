import json
from typing import List

import pandas as pd


class ProcTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame(columns=['proc_name', 'other_info'])
        else:
            for i in range(len(table.other_info)):
                json_data = table.other_info[i].replace("'", "\"")
                table.at[i, 'other_info'] = json.loads(json_data)
        self.table: pd.DataFrame = table

    def insert_proc(self, proc_name: str) -> int:
        self.table = self.table.append({'proc_name': proc_name, 'other_info': {}}, ignore_index=True)
        self.table = self.table.drop_duplicates('proc_name', ignore_index=True)
        return self.table.loc[self.table['proc_name'] == proc_name].index[0]

    def update_proc(self, proc_name: str, other_info: dict):
        self.table.loc[self.table['proc_name'] == proc_name]['other_info'][self.get_proc_index(proc_name)].update(
            other_info)

    def get_proc_name(self, index: int) -> str:
        return self.table.loc[index].proc_name

    def get_other_info(self, proc_name: str) -> dict:
        return self.table['other_info'][self.table.loc[self.table['proc_name'] == proc_name].index[0]]

    def get_proc_index(self, proc_name: str) -> int:
        return self.table.loc[self.table['proc_name'] == proc_name].index[0]

    def get_size(self) -> int:
        return len(self.table)

    def get_all_proc_name(self) -> List[str]:
        return self.table['proc_name'].tolist()

    def is_in(self, proc_name: str) -> bool:
        names: pd.Series = self.table['proc_name'] == proc_name
        for name in names:
            if name:
                return True
        return False

    def to_string(self) -> None:
        print("ProcTable:")
        print(self.table.to_string())

    def to_log(self) -> str:
        return "ProcTable: \n" + self.table.to_string()
