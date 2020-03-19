import argparse
import json
from typing import Dict

from aitsi_parser.Parser import Parser


def export_AST_to_file(json_ast: Dict[str, dict], filename: str = "AST.json") -> None:
    with open(filename, 'w') as f:
        json.dump(json_ast, f, indent=4, sort_keys=True)


def read_program_from_file(filename: str = "code_short.txt") -> Parser:
    with open(filename) as g:
        _parser: Parser = Parser(g.read())
        return _parser


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Aitsi parser!')
    arg_parser.add_argument("--i", default="code_short.txt", type=str, help="Input file with program")
    arg_parser.add_argument("--o", default="AST.json", type=str, help="Output file for AST json ")
    args: argparse.Namespace = arg_parser.parse_args()

    input_filename: str = args.i
    output_filename: str = args.o
    parser: Parser = read_program_from_file(input_filename)
    parser.program()

    json_tree: Dict[str, dict] = parser.get_node_json()
    print(json_tree)
    export_AST_to_file(json_tree, output_filename)
    parser.var_table.to_string()
    parser.mod_table.to_string()
