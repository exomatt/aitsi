import argparse
import json
import os
from typing import Dict

from aitsi_parser.CsvBuilder import CsvBuilder
from aitsi_parser.Parser import Parser


def export_AST_to_file(json_ast: Dict[str, dict], filename: str = "AST.json") -> None:
    with open(filename, 'w') as f:
        json.dump(json_ast, f, indent=4, sort_keys=True)


def read_program_from_file(filename: str = "code_short.txt") -> Parser:
    with open(filename) as g:
        _parser: Parser = Parser(g.read(), filename)
        return _parser


def main(simple_file_path: str = "code_short.txt", tree_output: str = "AST.json",
         output_directory: str = "test") -> str:
    parser: Parser = read_program_from_file(simple_file_path)
    parser.program()
    json_tree: Dict[str, dict] = parser.get_node_json()
    ##todo można odkomentować żeby wypisac sobie dane cyk najlepiej zmienic na logi
    # print(json_tree)
    # parser.var_table.to_string()
    # parser.proc_table.to_string()
    # parser.calls_table.to_string()
    # parser.mod_table.to_string()
    # parser.parent_table.to_string()
    # parser.uses_table.to_string()
    # parser.follows_table.to_string()
    # parser.statement_table.to_string()
    dirname, filename = os.path.split(os.path.abspath(__file__))
    path: str = os.path.join(dirname, "database/", output_directory, os.path.basename(simple_file_path).split('.')[0],
                             "")
    os.makedirs(path, exist_ok=True)
    export_AST_to_file(json_tree, path + tree_output)
    CsvBuilder.save_table_to_csv_file(parser.mod_table.table, path + "ModifiesTable.csv")
    CsvBuilder.save_table_to_csv_file(parser.var_table.table, path + "VarTable.csv")
    CsvBuilder.save_table_to_csv_file(parser.proc_table.table, path + "ProcTable.csv")
    CsvBuilder.save_table_to_csv_file(parser.calls_table.table, path + "CallsTable.csv")
    CsvBuilder.save_table_to_csv_file(parser.mod_table.table, path + "ModifiesTable.csv")
    CsvBuilder.save_table_to_csv_file(parser.parent_table.table, path + "ParentTable.csv")
    CsvBuilder.save_table_to_csv_file(parser.uses_table.table, path + "UsesTable.csv")
    CsvBuilder.save_table_to_csv_file(parser.follows_table.table, path + "FollowsTable.csv")
    CsvBuilder.save_table_to_csv_file(parser.statement_table.table, path + "StatementTable.csv")
    # todo - dodać resztę tabelek jak będą :*
    return path

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Aitsi parser!')
    arg_parser.add_argument("--i", default="code_short.txt", type=str, help="Input file with program")
    arg_parser.add_argument("--o", default="AST.json", type=str, help="Output file for AST json ")
    arg_parser.add_argument("--d", default="test", type=str, help="Name of output directory")
    args: argparse.Namespace = arg_parser.parse_args()
    input_filename: str = args.i
    tree_filename: str = args.o
    output_filename: str = args.d
    main(input_filename, tree_filename, output_filename)
