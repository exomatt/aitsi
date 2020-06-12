from typing import List, Union, Set, Tuple, Dict


class ResultsTable:

    def __init__(self) -> None:
        self.table: Dict = {}
        self.table['BOOLEAN'] = {}
        self.table['CONST'] = {}
        self.select: Tuple[str, str] = ('', '')

    def set_results(self, synonym: str, synonym_type: str):
        if synonym not in self.table.keys():
            self.table[synonym] = {}
            self.table[synonym]['type'] = synonym_type

    def update_results(self, relation: str, synonym: str, results: Union[Set[str], Set[int], int, str]) -> None:
        self.table[synonym][relation] = results
        if synonym != 'CONST':
            self.table[synonym]['final'] = results.intersection(
                *[result for result in self.table[synonym].values() if type(result) is set])
        self.table['BOOLEAN'][relation] = bool(results)
        self.table['BOOLEAN']['final'] = bool(results)
        # print(f'{relation}: {synonym}')
        # self.to_string()
        if not self.table['BOOLEAN']['final']:
            raise Exception

    def get_final_result(self, synonym: str) -> Union[Set[int], Set[str], None]:
        try:
            return self.table[synonym]['final']
        except Exception:
            return None

    def get_relations(self, synonym: str) -> List[str]:
        try:
            return list(self.table[synonym].keys())
        except Exception:
            return []

    def get_all_relations(self) -> List[str]:
        try:
            return list(set(sum([list(self.table[element].keys()) for element in self.table], [])))
        except Exception:
            return []

    def get_select(self, all_tables) -> str:
        try:
            if self.select[1] == 'BOOLEAN':
                return str(self.table[self.select[1]]['final']).lower()
            return ', '.join(map(str, self.table[self.select[1]]['final']))
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
        print(self.table)

    def to_log(self) -> str:
        return "ResultsTable: \n" + str(self.table)
