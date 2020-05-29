from typing import List, Union, Set

import pandas as pd


class ResultsTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame(columns=['BOOLEAN', 'CONST'], index=['type', 'final'])
        self.table: pd.DataFrame = table

    def set_results(self, synonym: str, synonym_type: str):
        if synonym not in self.table.columns.tolist():
            self.table[synonym] = 0
            self.table[synonym] = self.table[synonym].astype('object')
            self.table.at['type', synonym] = synonym_type

    def update_results(self, relation: str, synonym: str, results: Union[Set[str], Set[int], int, str]) -> None:
        if relation not in self.table.index.tolist():
            self.table.loc[relation] = 0
        self.table.at[relation, synonym] = results
        if synonym != 'CONST':
            self.table.at['final', synonym] = results.intersection(
                *[element for element in self.table[synonym].values if type(element) is set])
        self.table.at[relation, 'BOOLEAN'] = bool(results)
        self.table.at['final', 'BOOLEAN'] = bool(results)
        print(f'{relation}: {synonym}')
        self.to_string()
        if not self.table.loc['final', 'BOOLEAN']:
            raise Exception

    def get_relations(self, synonym: str) -> List[str]:
        try:  # FIXME
            return self.table.index[self.table[synonym] != 0].tolist()
        except Exception:
            return []

    def get_results(self, relation: str) -> List[str]:
        try:  # FIXME
            return self.table.columns[self.table.loc[relation] == 1].tolist()
        except Exception:
            return []

    def part_of_common(self, synonym: str) -> Union[Set[int], Set[str]]:
        return list(filter(lambda values: type(values) is set, self.table[synonym].values))[-1]

    # def __is_calls(self, call_procedure: str, receiving_procedure: str) -> bool:
    #     try:
    #         return bool(self.table.at[call_procedure, receiving_procedure])
    #     except Exception:
    #         return False

    def to_string(self) -> None:
        print("ResultsTable:")
        print(self.table.to_string())

    def to_log(self) -> str:
        return "ResultsTable: \n" + self.table.to_string()
