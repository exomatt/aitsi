import pandas as pd


class ProcTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame(columns=['proc_name', 'other_info'])
        self.table: pd.DataFrame = table

    def insert_proc(self, proc_name: str) -> int:
        self.table = self.table.append({'proc_name': proc_name, 'other_info': {}}, ignore_index=True)
        self.table = self.table.drop_duplicates('proc_name', ignore_index=True)
        return self.table.loc[self.table['proc_name'] == proc_name].index[0]

    def update_proc(self, proc_name: str, other_info: dict):
        self.table.loc[self.table['proc_name'] == proc_name]['other_info'][self.get_proc_index(proc_name)].update(other_info)

    def get_proc_name(self, index: int) -> str:
        return self.table.loc[index].proc_name

    def get_proc_index(self, proc_name: str) -> int:
        return self.table.loc[self.table['proc_name'] == proc_name].index[0]

    def get_size(self) -> int:
        return len(self.table)

    def is_in(self, proc_name: str) -> bool:
        names: pd.Series = self.table['proc_name'] == proc_name
        for name in names:
            if name:
                return True
        return False

    def to_string(self) -> None:
        print("ProcTable:")
        print(self.table.to_string())
