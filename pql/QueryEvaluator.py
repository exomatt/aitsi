import logging
from typing import List, Union, Dict, Tuple

from aitsi_parser.CallsTable import CallsTable
from aitsi_parser.FollowsTable import FollowsTable
from aitsi_parser.ModifiesTable import ModifiesTable
from aitsi_parser.ParentTable import ParentTable
from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.UsesTable import UsesTable
from aitsi_parser.VarTable import VarTable
from pql.Node import Node
from pql.relations.CallsRelation import CallsRelation
from pql.relations.FollowsRelation import FollowsRelation
from pql.relations.ModifiesRelation import ModifiesRelation
from pql.relations.ParentRelation import ParentRelation
from pql.relations.UsesRelation import UsesRelation

log = logging.getLogger(__name__)


class QueryEvaluator:
    relation = ['FOLLOWST', 'PARENTT', 'FOLLOWS', 'PARENT', 'MODIFIES', 'USES', 'CALLST', 'CALLS']
    argument = ['EVERYTHING', 'INTEGER', 'IDENT_QUOTE', 'IDENT']

    def __init__(self, code_ast_tree: Node, all_tables: Dict[str, Union[
        VarTable, ProcTable, UsesTable, ParentTable, ModifiesTable, FollowsTable, CallsTable, StatementTable]]) -> None:
        self.code_ast_tree: Node = code_ast_tree
        self.all_tables: Dict[str, Union[VarTable,
                                         ProcTable,
                                         UsesTable,
                                         ParentTable,
                                         ModifiesTable,
                                         FollowsTable,
                                         CallsTable,
                                         StatementTable]] = all_tables
        self.results: Union[bool, List[str], List[int]] = None
        self.select: Tuple[str, str] = None
        self.parameters_with: Dict[str, Tuple[str, Dict[str, str]]] = {}
        self.and_flag = False

    def evaluate_query(self, pql_ast_tree: Node) -> Union[bool, List[str], List[int]]:
        for node in pql_ast_tree.children:
            self.distribution_of_tasks(node)
        return self.results

    def distribution_of_tasks(self, root: Node) -> None:
        if root.node_type == 'RESULT':
            self.select = root.children[0].node_type, root.children[0].value
        elif root.node_type == 'SUCH_THAT':
            for node in root.children:
                self.relation_preparation(node)
        elif root.node_type == 'WITH':
            for node in root.children:
                self.attr_analysis(node)

    def relation_preparation(self, relation: Node) -> None:
        self.adding_relation_result_to_result(
            self.select_relation(
                relation.node_type,
                self.choosing_an_argument(relation.children[0]),
                self.choosing_an_argument(relation.children[1])),
            relation)

    def choosing_an_argument(self, argument_relation: Node) -> str:
        if argument_relation.node_type in ['INTEGER', 'EVERYTHING', 'IDENT_QUOTE']:
            return argument_relation.value
        else:
            return argument_relation.node_type

    def select_relation(self, relation_type: str, argument_first: str, argument_second: str) -> Union[
        Tuple[List[int], None], Tuple[List[str], None], Tuple[bool, None]]:
        if relation_type == 'MODIFIES':
            return ModifiesRelation(self.all_tables['modifies'], self.all_tables['var'],
                                    self.all_tables['statement'], self.all_tables['proc']) \
                .modifies(argument_first, argument_second)
        elif relation_type == 'USES':
            return UsesRelation(self.all_tables['uses'], self.all_tables['var'],
                                self.all_tables['statement'], self.all_tables['proc']) \
                .uses(argument_first, argument_second)
        elif relation_type == 'PARENT':
            return ParentRelation(self.all_tables['parent'], self.all_tables['statement']) \
                .parent(argument_first, argument_second)
        elif relation_type == 'PARENTT':
            return ParentRelation(self.all_tables['parent'], self.all_tables['statement']) \
                .parent_T(argument_first, argument_second)
        elif relation_type == 'FOLLOWS':
            return FollowsRelation(self.all_tables['follows'], self.all_tables['statement']) \
                .follows(argument_first, argument_second)
        elif relation_type == 'FOLLOWST':
            return FollowsRelation(self.all_tables['follows'], self.all_tables['statement']) \
                .follows_T(argument_first, argument_second)
        elif relation_type == 'CALLS':
            return CallsRelation(self.all_tables['calls'], self.all_tables['var'], self.all_tables['statement'],
                                 self.all_tables['proc']) \
                .calls(argument_first, argument_second)
        elif relation_type == 'CALLST':
            return CallsRelation(self.all_tables['calls'], self.all_tables['var'], self.all_tables['statement'],
                                 self.all_tables['proc']) \
                .calls_T(argument_first, argument_second)

    def adding_relation_result_to_result(self, relation_result: Union[
        Tuple[List[int], None], Tuple[List[str], None], Tuple[bool, None]], relation_node: Node):
        """
        łączenie danych przychodzacych z relacji w jedno odpowiedz
        :param relation_result: odpowiedz z reacji
        :param relation_node: analizowny Node relacji
        """
        if relation_result[1] is not None:
            if self.select[1] == relation_node.children[0].value:
                if self.results is not None:
                    self.results = list(set(self.results).intersection(set(relation_result[0])))
                else:
                    self.results = relation_result[0]
            elif self.select[1] == relation_node.children[1].value:
                if self.results is not None:
                    self.results = list(set(self.results).intersection(set(relation_result[1])))
                else:
                    self.results = relation_result[1]
        else:
            if self.results is not None:
                self.results = list(set(self.results).intersection(set(relation_result[0])))
            else:
                self.results = relation_result[0]

    def attr_analysis(self, attr_node: Node) -> None:
        self.parameters_with[attr_node.children[0].value] = (
            (attr_node.children[0].node_type, self.right_side(attr_node.children[1])))

    def right_side(self, right_node: Node) -> Dict[str, str]:
        return {'type': right_node.node_type, 'variable_name': right_node.value}
