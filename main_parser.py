import argparse
import json
import os
from typing import Dict

from aitsi_parser.CsvBuilder import CsvBuilder
from aitsi_parser.Parser import Parser
from pql.relations.ParentRelation import ParentRelation


def export_AST_to_file(json_ast: Dict[str, dict], filename: str = "AST.json") -> None:
    with open(filename, 'w') as f:
        json.dump(json_ast, f, indent=4, sort_keys=True)


def read_program_from_file(filename: str = "code_short.txt") -> Parser:
    with open(filename) as g:
        _parser: Parser = Parser(g.read(), filename)
        return _parser


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Aitsi parser!')
    arg_parser.add_argument("--i", default="code_short.txt", type=str, help="Input file with program")
    arg_parser.add_argument("--o", default="AST.json", type=str, help="Output file for AST json ")
    arg_parser.add_argument("--d", required=True, type=str, help="Name of output directory")
    args: argparse.Namespace = arg_parser.parse_args()

    input_filename: str = args.i
    output_filename: str = args.o
    output_directory: str = args.d
    parser: Parser = read_program_from_file(input_filename)
    parser.program()

    json_tree: Dict[str, dict] = parser.get_node_json()
    print(json_tree)
    export_AST_to_file(json_tree, output_filename)
    parser.var_table.to_string()
    parser.proc_table.to_string()
    parser.calls_table.to_string()
    parser.mod_table.to_string()
    parser.parent_table.to_string()
    parser.uses_table.to_string()
    parser.follows_table.to_string()
    parser.statement_table.to_string()
    dirname, filename = os.path.split(os.path.abspath(__file__))

    path: str = os.path.join(dirname, "database/", output_directory, os.path.basename(input_filename).split('.')[0],
                             "")
    os.makedirs(path, exist_ok=True)

    print("---------------------")
    parser.parent_table.to_string()
    print("---------------------")
    parent_rel: ParentRelation = ParentRelation(parser.root, parser.parent_table)
    test_1 = parent_rel.parent("8", "10")
    test_2 = parent_rel.parent("10", "11")
    test_3 = parent_rel.parent("8", "_")
    test_4 = parent_rel.parent("8", "CALL")
    test_5 = parent_rel.parent("8", "STMT")
    test_1T = parent_rel.parent_T("8", "11")
    test_3T = parent_rel.parent_T("8", "_")

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
