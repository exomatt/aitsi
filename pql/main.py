import argparse
import json
from typing import Dict

from pql.Node import Node
from pql.QueryProcessor import QueryProcessor
from pql.relations.ModifiesRelation import ModifiesRelation
from pql.relations.ParentRelation import ParentRelation


def load_ast_from_file(filename: str) -> Node:
    with open(filename) as g:
        loaded_node: Node = Node.Schema().loads(g.read())
        return loaded_node


def load_query_from_file(filename: str) -> str:
    with open(filename) as g:
        _query: str = g.read()
        return _query


def export_query_tree_to_file(query_json_tree: Dict[str, dict], filename: str = "pql_query_tree.json") -> None:
    with open(filename, 'w') as f:
        json.dump(query_json_tree, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='PQL program!')
    arg_parser.add_argument("--i", default="pql_query.txt", type=str, help="Input file with pql query")
    arg_parser.add_argument("--o", default="pql_query_tree.json", type=str, help="Output file for pql query tree ")
    arg_parser.add_argument("--ast", default="AST.json", type=str, help="Input file with AST tree")
    args: argparse.Namespace = arg_parser.parse_args()
    input_query_filename: str = args.i
    input_ast_filename: str = args.ast
    output_query_filename: str = args.o

    ast_node: Node = load_ast_from_file(input_ast_filename)
    parent_rel: ParentRelation = ParentRelation(ast_node)
    is_parent: bool = parent_rel.parent('8', '9')
    test_1 = parent_rel.parent('8', '_')
    test_2 = parent_rel.parent('8', 'CALL')
    test_3 = parent_rel.parent('8', 'WHILE')

    test_4 = parent_rel.parent('IF', '18')
    test_5 = parent_rel.parent('_', '9')
    test_6 = parent_rel.parent('_', '_')
    test_7 = parent_rel.parent('_', 'CALL')
    test_8 = parent_rel.parent('IF', 'CALL')
    test_9 = parent_rel.parent('_', 'ASSIGN')
    test_10 = parent_rel.parent('_', 'WHILE')
    test_11 = parent_rel.parent('IF', '_')
    modifies_rel: ModifiesRelation = ModifiesRelation(ast_node)
    mod_test_1 = modifies_rel.modifies('1', 't')
    mod_test_2 = modifies_rel.modifies('2', 't')
    mod_test_3 = modifies_rel.modifies('3', 'd')
    mod_test_4 = modifies_rel.modifies('3', '_')
    mod_test_5 = modifies_rel.modifies('8', '_')
    mod_test_6 = modifies_rel.modifies('3', 'VARIABLE')
    mod_test_7 = modifies_rel.modifies('_', 'd')
    mod_test_8 = modifies_rel.modifies('IF', '_')
    mod_test_9 = modifies_rel.modifies('IF', 'VARIABLE')
    mod_test_10 = modifies_rel.modifies('IF', '_')
    mod_test_11 = modifies_rel.modifies('_', '_')
    mod_test_12 = modifies_rel.modifies('IF', 'a')
    mod_test_13 = modifies_rel.modifies('WHILE', 'VARIABLE')
    mod_test_14 = modifies_rel.modifies('WHILE', 'd')
    mod_test_15 = modifies_rel.modifies('_', 'VARIABLE')
    mod_test_16 = modifies_rel.modifies('_', 'i')

    query: str = load_query_from_file(input_query_filename)

    parser: QueryProcessor = QueryProcessor()
    parser.generate_query_tree(query)
    query_tree: Dict[str, dict] = parser.get_node_json()

    export_query_tree_to_file(query_tree)
