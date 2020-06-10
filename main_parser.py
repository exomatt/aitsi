import argparse
import json
import logging
import logging.config as conf
import os
import time
from typing import Dict

from aitsi_parser.JsonBuilder import JsonBuilder
from aitsi_parser.Parser import Parser

log = logging.getLogger(__name__)


def export_AST_to_file(json_ast: Dict[str, dict], filename: str = "AST.json") -> None:
    with open(filename, 'w') as f:
        json.dump(json_ast, f, indent=4, sort_keys=True)


def read_program_from_file(filename: str = "code_short.txt") -> Parser:
    with open(filename) as g:
        _parser: Parser = Parser(g.read(), filename)
        return _parser


def main(simple_file_path: str = "code_short.txt", tree_output: str = "AST.json",
         output_directory: str = "test") -> str:
    current = time.time()
    parser: Parser = read_program_from_file(simple_file_path)
    parser.program()
    dirname, filename = os.path.split(os.path.abspath(__file__))
    path: str = os.path.join(dirname, "database/", output_directory, os.path.basename(simple_file_path).split('.')[0],
                             "")
    os.makedirs(path, exist_ok=True)
    export_AST_to_file(parser.get_node_json(), path + tree_output)
    JsonBuilder.save_table_to_json_file([{'variable_name': key, 'other_info': {}} for key in parser.var_table],
                                        path + "VarTable.json")
    JsonBuilder.save_table_to_json_file(parser.proc_table, path + "ProcTable.json")
    JsonBuilder.save_table_to_json_file(parser.statement_table, path + "StatementTable.json")
    JsonBuilder.save_table_to_json_file(parser.const_table, path + "ConstTable.json")
    JsonBuilder.save_table_to_json_file(parser.follows_table, path + "FollowsTable.json")
    JsonBuilder.save_table_to_json_file(parser.parent_table, path + "ParentTable.json")
    JsonBuilder.save_table_to_json_file(parser.calls_table, path + "CallsTable.json")
    JsonBuilder.save_table_to_json_file(parser.next_table, path + "NextTable.json")
    JsonBuilder.save_table_to_json_file(parser.mod_table, path + "ModifiesTable.json")
    JsonBuilder.save_table_to_json_file(parser.uses_table, path + "UsesTable.json")
    # todo - dodać resztę tabelek jak będą :*
    # print(time.time() - current)
    return path


if __name__ == '__main__':
    conf.fileConfig("logging.conf", disable_existing_loggers=False)
    arg_parser = argparse.ArgumentParser(description='Aitsi parser!')
    arg_parser.add_argument("--i", default="code_short.txt", type=str, help="Input file with program")
    arg_parser.add_argument("--o", default="AST.json", type=str, help="Output file for AST json ")
    arg_parser.add_argument("--d", default="test", type=str, help="Name of output directory")
    args: argparse.Namespace = arg_parser.parse_args()
    input_filename: str = args.i
    tree_filename: str = args.o
    output_filename: str = args.d
    main(input_filename, tree_filename, output_filename)
