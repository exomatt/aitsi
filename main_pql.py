import argparse
import json
from typing import Dict

from aitsi_parser.CallsTable import CallsTable
from aitsi_parser.FollowsTable import FollowsTable
from aitsi_parser.ModifiesTable import ModifiesTable
from aitsi_parser.ParentTable import ParentTable
from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.UsesTable import UsesTable
from aitsi_parser.VarTable import VarTable
from pql.Node import Node
from pql.QueryEvaluator import QueryEvaluator
from pql.QueryProcessor import QueryProcessor
from pql.utils.CsvReader import CsvReader


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


def main():

    input_query_filename: str = "pql_query.txt"
    input_ast_filename: str = "pql_query_tree.json"
    output_query_filename: str = "AST.json"
    tables_directory_path: str = "database/test/code_short"

    ast_node: Node = load_ast_from_file(input_ast_filename)

    var_table: VarTable = VarTable(CsvReader.read_csv_from_file(tables_directory_path + "/VarTable.csv"))
    proc_table: ProcTable = ProcTable(CsvReader.read_csv_from_file(tables_directory_path + "/ProcTable.csv"))
    calls_table: CallsTable = CallsTable(
        CsvReader.read_csv_from_file(tables_directory_path + "/CallsTable.csv"))
    modifies_table: ModifiesTable = ModifiesTable(
        CsvReader.read_csv_from_file(tables_directory_path + "/ModifiesTable.csv"))
    parent_table: ParentTable = ParentTable(
        CsvReader.read_csv_from_file(tables_directory_path + "/ParentTable.csv", True))
    uses_table: UsesTable = UsesTable(CsvReader.read_csv_from_file(tables_directory_path + "/UsesTable.csv"))
    follows_table: FollowsTable = FollowsTable(
        CsvReader.read_csv_from_file(tables_directory_path + "/FollowsTable.csv", True))
    statement_table: StatementTable = StatementTable(
        CsvReader.read_csv_from_file(tables_directory_path + "/StatementTable.csv"))
    all_tables: Dict[str, object] = {'var': var_table, 'proc': proc_table, 'uses': uses_table, 'parent': parent_table,
                                     'modifies': modifies_table, 'follows': follows_table, 'calls': calls_table,
                                     'statement': statement_table}

    query: str = load_query_from_file(input_query_filename)

    query_processor: QueryProcessor = QueryProcessor()
    query_processor.generate_query_tree(query)
    query_tree: Dict[str, dict] = query_processor.get_node_json()

    query_evaluator: QueryEvaluator = QueryEvaluator(ast_node, all_tables)
    response = query_evaluator.evaluate_query(query_processor.root)
    print(response)

    export_query_tree_to_file(query_tree)
