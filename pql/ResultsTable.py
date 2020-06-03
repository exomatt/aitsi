from typing import List, Union, Set, Tuple

import pandas as pd

from pql.Reference import Reference


class ResultsTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame(columns=['BOOLEAN', 'CONST'], index=['type', 'final'])
        self.table: pd.DataFrame = table
        self.select: Tuple[str, str] = ('', '')

    def set_results(self, synonym: str, synonym_type: str):
        if synonym not in self.table.columns.tolist():
            self.table[synonym] = 0
            self.table[synonym] = self.table[synonym].astype('object')
            self.table.at['type', synonym] = synonym_type

    def update_results(self, relation: str, synonym: str, results: Union[Set[Reference], str]) -> None:
        if relation not in self.table.index.tolist():
            self.table.loc[relation] = 0
        self.table.at[relation, synonym] = results
        if synonym != 'CONST':
            inter_table = self.table.loc[set(self.table.index.tolist()) - {'final', 'WITH', 'PATTERN', 'type'}]
            if not inter_table.empty:
                self.table.at['final', synonym] = results.intersection(
                    *[element for element in inter_table[synonym] if type(element) is set])
            else:
                self.table.at['final', synonym] = results.intersection(
                    *[element for element in self.table[synonym].values if type(element) is set])
        self.table.at[relation, 'BOOLEAN'] = bool(results)
        self.table.at['final', 'BOOLEAN'] = bool(results)
        # print(f'{relation}: {synonym}')
        # self.to_string()
        if not self.table.loc['final', 'BOOLEAN']:
            raise Exception

    def get_final_result(self, synonym: str) -> Set[Reference]:
        try:
            return self.table.at['final', synonym]
        except Exception:
            return None

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

    def get_select(self, all_tables) -> str:
        try:
            if self.select[1] == 'BOOLEAN':
                return str(self.table.at['final', self.select[1]]).lower()
            return ', '.join({element.element for element in self.table.at['final', self.select[1]]})
        except:
            if self.select[0] in ['STMT', 'PROG_LINE']:
                return ', '.join(map(str, all_tables['statement'].get_all_statement_lines()))
            elif self.select[0] == 'PROCEDURE':
                return ', '.join(all_tables['proc'].get_all_proc_name())
            elif self.select[0] == 'VARIABLE':
                return ', '.join(all_tables['var'].get_all_var_name())
            elif self.select[0] == 'CONSTANT':
                return ', '.join(map(str, all_tables['const'].get_all_constant()))
            else:
                return ', '.join(
                    map(str, all_tables['statement'].get_statement_line_by_type_name(self.select[0])))

    def to_string(self) -> None:
        print("ResultsTable:")
        print(self.table.to_string())

    def to_log(self) -> str:
        return "ResultsTable: \n" + self.table.to_string()
