import argparse
import json
from typing import Dict

from pql.Node import Node
from pql.QueryEvaluator import QueryEvaluator
from pql.QueryProcessor import QueryProcessor
from pql.relations.ParentRelation import ParentRelation
from pql.relations.FollowsRelation import FollowsRelation


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
    # parent_rel: ParentRelation = ParentRelation(ast_node)
    # is_parent: bool = parent_rel.parent('8', '9')
    # test_1 = parent_rel.parent('8', '_')
    # test_2 = parent_rel.parent('8', 'CALL')
    # test_3 = parent_rel.parent('8', 'WHILE')
    #
    # test_4 = parent_rel.parent('IF', '18')
    # test_5 = parent_rel.parent('_', '9')
    # test_6 = parent_rel.parent('_', '_')
    # test_7 = parent_rel.parent('_', 'CALL')
    # test_8 = parent_rel.parent('IF', 'CALL')
    # test_9 = parent_rel.parent('_', 'ASSIGN')
    # test_10 = parent_rel.parent('_', 'WHILE')
    # test_11 = parent_rel.parent('IF', '_')

    follows_rel: FollowsRelation = FollowsRelation(ast_node)
    test_1 = follows_rel.follows('9', '10')
    test_2 = follows_rel.follows('9', '13')
    test_3 = follows_rel.follows('9', 'WHILE')
    test_4 = follows_rel.follows('9', 'ASSIGN')
    test_5 = follows_rel.follows('2', 'ASSIGN')
    test_6 = follows_rel.follows('7', '_')
    test_7 = follows_rel.follows('2', '_')
    test_8 = follows_rel.follows('WHILE', '13')
    test_9 = follows_rel.follows('ASSIGN', '9')
    test_10 = follows_rel.follows('ASSIGN', '2')
    test_11 = follows_rel.follows('_', '7')
    test_12 = follows_rel.follows('_', '2')
    test_13 = follows_rel.follows('WHILE', 'ASSIGN')
    test_14 = follows_rel.follows('ASSIGN', 'WHILE')
    test_15 = follows_rel.follows('_', '_')

    query: str = load_query_from_file(input_query_filename)

    query_processor: QueryProcessor = QueryProcessor()
    query_processor.generate_query_tree(query)
    query_tree: Dict[str, dict] = query_processor.get_node_json()

    query_evaluator: QueryEvaluator = QueryEvaluator()
    response = query_evaluator.generate_result(query_processor.root, ast_node)
    print(response)

    export_query_tree_to_file(query_tree)
