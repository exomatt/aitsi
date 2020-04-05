from typing import List, Union, Dict, Tuple

from pql.Node import Node
from pql.relations.FollowsRelation import FollowsRelation
from pql.relations.ModifiesRelation import ModifiesRelation
from pql.relations.ParentRelation import ParentRelation
from pql.relations.UsesRelation import UsesRelation
from pql.utils.SearchUtils import SearchUtils


class QueryEvaluator:
    relation = ['FOLLOWST', 'PARENTT', 'FOLLOWS', 'PARENT', 'MODIFIES', 'USES', 'CALLST', 'CALLS']
    argument = ['EVERYTHING', 'INTEGER', 'IDENT_QUOTE', 'IDENT']

    def __init__(self, code_ast_tree: Node, all_tables: Dict[str, object]) -> None:
        self.variables: Node = None
        self.code_ast_tree: Node = code_ast_tree
        self.all_tables: Dict[str, object] = all_tables
        self.result: Union[bool, List[str], List[int]] = None
        self.select: str = None
        self.parameter_with: Tuple[str, str] = ['', '']
        self.and_flag = False

    def evaluate_query(self, pql_ast_tree: Node) -> Union[bool, List[str], List[int]]:
        self.node_analysis(pql_ast_tree)
        self.find_line_of_select_variable()
        return self.result

    def find_line_of_select_variable(self) -> None:
        if self.select != 'STMT' and type(self.result) != bool and self.select != 'VARIABLE':
            search_node: List[int] = SearchUtils(self.code_ast_tree).find_node_line_number_by_type(self.select)
            self.result = list(set(self.result).intersection(search_node))

    def node_analysis(self, root: Node) -> None:
        if root.node_type in self.relation:
            self.select_relation(root.node_type,
                                 self.arguments_analysis(root.children[0]), self.arguments_analysis(root.children[1]))
            if len(root.children) == 3:
                self.and_flag = True
                self.node_analysis(root.children[2])
        elif root.node_type == 'DECLARATION':
            self.variables = root
        elif root.node_type == 'RESULT':
            if root.children[0].node_type == 'BOOLEAN':
                self.select = root.children[0].node_type
            else:
                self.select = self.variable_search(root.children[0].value)
        elif root.node_type == 'WITH' and self.parameter_with[0] == '':
            self.with_analysis(root)
        else:
            for index in range(len(root.children)):
                if root.children[index].node_type == 'SUCH_THAT' and len(root.children) != index + 1:
                    self.with_analysis(root.children[index + 1])
                self.node_analysis(root.children[index])

    def arguments_analysis(self, argument_relation: Node) -> str:
        if argument_relation.node_type in ['INTEGER', 'EVERYTHING', 'IDENT_QUOTE']:
            return argument_relation.value
        elif argument_relation.node_type == 'IDENT':
            return self.variable_search(argument_relation.value)

    def variable_search(self, value: str) -> str:
        if value == self.parameter_with[0]:
            return self.parameter_with[1]
        for parent in self.variables.children:
            for child in parent.children:
                if child.value == value:
                    return parent.node_type

    def select_relation(self, relation_type: str, argument_first: str, argument_second: str):
        if relation_type == 'MODIFIES':
            result_relation = ModifiesRelation(self.all_tables['modifies'], self.all_tables['var'],
                                               self.all_tables['statement'], self.all_tables['proc']).modifies(
                argument_first, argument_second)
        elif relation_type == 'USES':
            result_relation = UsesRelation(self.all_tables['uses'], self.all_tables['var'],
                                           self.all_tables['statement'], self.all_tables['proc']).uses(
                argument_first,
                argument_second)
        elif relation_type == 'PARENT':
            result_relation = ParentRelation(self.all_tables['parent'], self.all_tables['statement']).parent(
                argument_first,
                argument_second)
        elif relation_type == 'PARENTT':
            result_relation = ParentRelation(self.all_tables['parent'], self.all_tables['statement']).parent_T(
                argument_first,
                argument_second)
        elif relation_type == 'FOLLOWS':
            result_relation = FollowsRelation(self.all_tables['follows'], self.all_tables['statement']).follows(
                argument_first,
                argument_second)
        elif relation_type == 'FOLLOWST':
            result_relation = FollowsRelation(self.all_tables['follows'], self.all_tables['statement']).follows_T(
                argument_first,
                argument_second)

        if self.and_flag:
            self.result = list(set(self.result).intersection(result_relation))
        else:
            self.result = result_relation

    def with_analysis(self, with_node: Node) -> None:
        value_node: Node = with_node.children[0]
        self.parameter_with = (value_node.value, self.variable_search(value_node.value))
        self.resolve_attribute(value_node.children[0])

    def resolve_attribute(self, node: Node) -> None:
        if (self.parameter_with[1] == 'STMT' and node.value == 'stmt#') or (
                self.parameter_with[1] in ['PROCEDURE', 'CALL'] and node.value == 'procName') or (
                self.parameter_with[1] == 'VARIABLE' and node.value == 'varName') or (
                self.parameter_with[1] == 'CONSTANT' and node.value == 'value'):
            self.substitute_value(node.children[0])
        else:
            print('ERROR')

    def substitute_value(self, value_node: Node) -> None:
        self.parameter_with = (self.parameter_with[0], value_node.value)
