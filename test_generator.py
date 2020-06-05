import os
import random

from aitsi_parser.ConstTable import ConstTable
from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.VarTable import VarTable
from pql.utils.CsvReader import CsvReader


class Generator:

    def __init__(self, path_tables: str):
        self.relation: str = ''
        self.path_tests: str = 'tests/generate'
        if not os.path.exists(self.path_tests):
            os.makedirs(self.path_tests)
        self.arguments_in_relation = {
            'Next': ['prog_line'],
            'Next*': ['prog_line'],
            'Follows': ['stmt', 'while', 'if', 'call', 'assign'],
            'Follows*': ['stmt', 'while', 'if', 'call', 'assign'],
            'Parent': ['stmt', 'while', 'if', 'call', 'assign'],
            'Parent*': ['stmt', 'while', 'if', 'call', 'assign'],
            'Modifies': ['stmt', 'while', 'if', 'call', 'assign', 'procedure'],
            'Uses': ['stmt', 'while', 'if', 'call', 'assign', 'procedure'],
            'Calls': ['procedure'],
            'Calls*': ['procedure'],
        }
        self.var_table: VarTable = VarTable(CsvReader.read_csv_from_file(path_tables + "/VarTable.csv"))
        self.proc_table: ProcTable = ProcTable(CsvReader.read_csv_from_file(path_tables + "/ProcTable.csv"))
        self.const_table: ConstTable = ConstTable(CsvReader.read_csv_from_file(path_tables + "/ConstTable.csv"))
        self.stmt_table: StatementTable = StatementTable(
            CsvReader.read_csv_from_file(path_tables + "/StatementTable.csv"))

    def _generate_single_relation(self, relation: str, f):
        for varname in self.arguments_in_relation[relation]:
            if relation in ['Modifies', 'Uses']:
                f.write(f'{varname} a; variable a1;\n')
                f.write(f'Select a such that {relation}(a,a1)\n')
                f.write('none\n')
                f.write(f'{varname} a; variable a1;\n')
                f.write(f'Select a1 such that {relation}(a,a1)\n')
                f.write('none\n')
                f.write(f'{varname} a; variable a1;\n')
                f.write(f'Select BOOLEAN such that {relation}(a,a1)\n')
                f.write('none\n')

                var = self.random_stmt_lines(self.var_table.get_all_var_name())
                for variable_name in var:
                    f.write(f'{varname} a;\n')
                    f.write(f'Select a such that {relation}(a,"{variable_name}")\n')
                    f.write('none\n')
                    f.write(f'{varname} a; variable a1;\n')
                    f.write(f'Select a such that {relation}(a,a1) with a1.varName="{variable_name}"\n')
                    f.write('none\n')
                    f.write(f'{varname} a; variable a1;\n')
                    f.write(f'Select a1 such that {relation}(a,a1) with a1.varName="{variable_name}"\n')
                    f.write('none\n')
                    f.write(f'{varname} a; variable a1;\n')
                    f.write(f'Select BOOLEAN such that {relation}(a,a1) with a1.varName="{variable_name}"\n')
                    f.write('none\n')

                if varname == 'procedure':
                    proc = self.random_stmt_lines(self.proc_table.get_all_proc_name())
                    for proc_name in proc:
                        f.write(f'variable a1;\n')
                        f.write(f'Select a1 such that {relation}("{proc_name}", a1)\n')
                        f.write('none\n')
                        f.write(f'{varname} a; variable a1;\n')
                        f.write(f'Select a such that {relation}(a,a1) with a.procName="{proc_name}"\n')
                        f.write('none\n')
                        f.write(f'{varname} a; variable a1;\n')
                        f.write(f'Select a1 such that {relation}(a,a1) with a.procName="{proc_name}"\n')
                        f.write('none\n')
                        f.write(f'{varname} a; variable a1;\n')
                        f.write(f'Select BOOLEAN such that {relation}(a,a1) with a.procName="{proc_name}"\n')
                        f.write('none\n')
                else:
                    list_lines = self.random_stmt_lines(self.stmt_table.get_all_statement_lines()[::5])
                    for stmt_line in list_lines:
                        f.write(f'variable a1;\n')
                        f.write(f'Select a1 such that {relation}({stmt_line}, a1)\n')
                        f.write('none\n')
                        f.write(f'{varname} a; variable a1;\n')
                        f.write(f'Select a such that {relation}(a,a1) with a.stmt#={stmt_line}\n')
                        f.write('none\n')
                        f.write(f'{varname} a; variable a1;\n')
                        f.write(f'Select a1 such that {relation}(a,a1) with a.stmt#={stmt_line}\n')
                        f.write('none\n')
                        f.write(f'{varname} a; variable a1;\n')
                        f.write(f'Select BOOLEAN such that {relation}(a,a1) with a.stmt#={stmt_line}\n')
                        f.write('none\n')
            else:
                for varname_second in self.arguments_in_relation[relation][::2]:
                    f.write(f'{varname_second} a1;\n')
                    f.write(f'Select BOOLEAN such that {relation}(_,a1)\n')
                    f.write('none\n')
                    f.write(f'{varname} a; {varname_second} a1;\n')
                    f.write(f'Select a1 such that {relation}(a,a1)\n')
                    f.write('none\n')
                    f.write(f'{varname} a; {varname_second} a1;\n')
                    f.write(f'Select a such that {relation}(a,a1)\n')
                    f.write('none\n')
                    f.write(f'{varname} a; {varname_second} a1;\n')
                    f.write(f'Select BOOLEAN such that {relation}(a,a1)\n')
                    f.write('none\n')
                    if varname == 'procedure':
                        proc = self.random_stmt_lines(self.proc_table.get_all_proc_name())
                        for proc_name in proc:
                            f.write(f'{varname} a1;\n')
                            f.write(f'Select a1 such that {relation}("{proc_name}", a1)\n')
                            f.write('none\n')
                            f.write(f'{varname} a; {varname_second} a1;\n')
                            f.write(f'Select a such that {relation}(a,a1) with a.procName="{proc_name}"\n')
                            f.write('none\n')
                            f.write(f'{varname} a; {varname_second} a1;\n')
                            f.write(f'Select a1 such that {relation}(a,a1) with a.procName="{proc_name}"\n')
                            f.write('none\n')
                            f.write(f'{varname} a; {varname_second} a1;\n')
                            f.write(f'Select BOOLEAN such that {relation}(a,a1) with a1.procName="{proc_name}"\n')
                            f.write('none\n')
                    elif varname == 'prog_line':
                        list_lines = self.random_stmt_lines(self.stmt_table.get_all_statement_lines()[::5])
                        for stmt_line in list_lines:
                            f.write(f'{varname} a1;\n')
                            f.write(f'Select a1 such that {relation}({stmt_line}, a1)\n')
                            f.write('none\n')
                            f.write(f'{varname} a1;\n')
                            f.write(f'Select a1 such that {relation}({stmt_line}, {stmt_line + 1})\n')
                            f.write('none\n')
                            f.write(f'{varname} a; {varname_second} a1;\n')
                            f.write(f'Select a such that {relation}(a,a1) with a={stmt_line}\n')
                            f.write('none\n')
                            f.write(f'{varname} a; {varname_second} a1;\n')
                            f.write(f'Select a1 such that {relation}(a,a1) with a={stmt_line}\n')
                            f.write('none\n')
                            f.write(f'{varname} a; {varname_second} a1;\n')
                            f.write(
                                f'Select a1 such that {relation}(a,a1) with a={stmt_line} and a1={stmt_line + 1}\n')
                            f.write('none\n')
                            f.write(f'{varname} a; {varname_second} a1;\n')
                            f.write(f'Select BOOLEAN such that {relation}(a,a1) with a1={stmt_line}\n')
                            f.write('none\n')
                    else:
                        list_lines = self.random_stmt_lines(self.stmt_table.get_all_statement_lines()[::5])
                        for stmt_line in list_lines:
                            f.write(f'{varname} a1;\n')
                            f.write(f'Select a1 such that {relation}({stmt_line}, a1)\n')
                            f.write('none\n')
                            f.write(f'{varname} a1;\n')
                            f.write(f'Select a1 such that {relation}({stmt_line}, {stmt_line + 1})\n')
                            f.write('none\n')
                            f.write(f'{varname} a; {varname_second} a1;\n')
                            f.write(f'Select a such that {relation}(a,a1) with a.stmt#={stmt_line}\n')
                            f.write('none\n')
                            f.write(f'{varname} a; {varname_second} a1;\n')
                            f.write(f'Select a1 such that {relation}(a,a1) with a.stmt#={stmt_line}\n')
                            f.write('none\n')
                            f.write(f'{varname} a; {varname_second} a1;\n')
                            f.write(
                                f'Select a1 such that {relation}(a,a1) with a.stmt#={stmt_line} and a1.stmt#={stmt_line + 1}\n')
                            f.write('none\n')
                            f.write(f'{varname} a; {varname_second} a1;\n')
                            f.write(f'Select BOOLEAN such that {relation}(a,a1) with a1.stmt#={stmt_line}\n')
                            f.write('none\n')

            f.write(f'{varname} a;\n')
            f.write(f'Select a such that {relation}(a,_)\n')
            f.write('none\n')
        if relation in ['Modifes', 'Uses']:
            f.write(f'variable a;\n')
            f.write(f'Select a such that {relation}(_,a)\n')
            f.write('none\n')

    def test_for_relation(self, relation: str = None, all: bool = False) -> None:
        self.relation = relation
        if all:
            with open(f'{self.path_tests}/all.txt', 'w') as f:
                for relation in ['Modifies', 'Uses', 'Follows', 'Follows*', 'Parent', 'Parent*', 'Next*', 'Next',
                                 'Calls',
                                 'Calls*']:
                    self._generate_single_relation(relation, f)
        else:
            if relation is not None:
                with open(f'{self.path_tests}/{relation.lower().replace("*", "_T")}.txt', 'w') as f:
                    self._generate_single_relation(relation, f)

    def random_stmt_lines(self, line_range, seed=0.06):
        return random.sample(line_range, int(len(line_range) * seed))


if __name__ == '__main__':
    run = True
    print('Path to the tables: ')
    path: str = input()
    generator: Generator = Generator(path)
    while run:
        print('1. Generate relation\n'
              '2. Generate multi relation\n'
              '3. Generate "with"\n'
              '4. Generate "pattern"\n'
              '5. Generate all\n'
              '6. Exit\n'
              '\n'
              'Choose number: ')
        commend: int = int(input())
        if commend == 1:
            print('Name relation: ')
            relation: str = input()
            if relation in ['Modifies', 'Uses', 'Follows', 'Follows*', 'Parent', 'Parent*', 'Next*', 'Next', 'Calls',
                            'Calls*']:
                generator.test_for_relation(relation)
                print('Finish')
            else:
                print('Incorrect relation')
        elif commend == 2:
            pass
        elif commend == 3:
            pass
        elif commend == 4:
            pass
        elif commend == 5:
            generator.test_for_relation(all=True)
            print('Finish')
        elif commend == 6:
            print('Bye ;*')
            run = False
