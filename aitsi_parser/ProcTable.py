from typing import List, Union, Dict


class ProcTable:

    def __init__(self, table: Union[Dict, List]) -> None:
        self.table: Union[Dict, List] = table

    def get_all_proc_name(self) -> List[str]:
        return [element['proc_name'] for element in self.table]

    def get_other_info(self, proc_name: str) -> dict:
        for element in self.table:
            if element['proc_name'] == proc_name:
                return element['other_info']

    def get_size(self) -> int:
        return len(self.table)

    def is_in(self, proc_name: str) -> bool:
        for name in self.table:
            if name['proc_name'] == proc_name:
                return True
        return False

    def to_string(self) -> None:
        print("ProcTable:")
        print(self.table)

    def to_log(self) -> str:
        return "ProcTable: \n" + str(self.table)
