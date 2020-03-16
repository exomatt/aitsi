from typing import List

from pql.Node import Node


class QueryEvaluator:
    relation = ['FOLLOWST', 'PARENTT', 'FOLLOWS', 'PARENT', 'MODIFIES', 'USES', 'CALLST', 'CALLS']
    argument = ['EVERYTHING', 'INTEGER', 'IDENT_QUOTE', 'IDENT']

    def __init__(self) -> None:
        self.declaration: Node = None
        self.code_tree: Node = None
        self.result: List[int] = None
        self.is_and = False

    def generate_result(self, pql_tree: Node, code_tree: Node) -> str:
        self.code_tree = code_tree
        self.node_analysis(pql_tree)

        return self.result

    def node_analysis(self, root: Node) -> None:
        if root.node_type in self.relation:
            self.select_relation(root.node_type,
                                 self.arguments_analysis(root.children[0]), self.arguments_analysis(root.children[1]))
            if len(root.children) == 3:
                self.is_and = True
                self.node_analysis(root.children[2])
        elif root.node_type == "DECLARATION":
            self.declaration = root
        else:
            for node in root.children:
                self.node_analysis(node)

    def arguments_analysis(self, argument_relation: Node) -> str:
        if argument_relation.node_type == 'INTEGER' or argument_relation.node_type == 'IDENT_QUOTE' or argument_relation.node_type == 'EVERYTHING':
            return argument_relation.value
        elif argument_relation.node_type == 'IDENT':
            for parent in self.declaration.children:
                for child in parent.children:
                    if child.value == argument_relation.value:
                        return parent.node_type

    def select_relation(self, relation_type: str, argument_first: str, argument_second: str):
        if relation_type == 'MODIFIES':
            result_relation = ModifiesRelation(self.code_tree).modifices(argument_first, argument_second)
        elif relation_type == 'USES':
            result_relation = UsesRelation(self.code_tree).uses(argument_first, argument_second)
        elif relation_type == 'PARENT':
            result_relation = ParentRelation(self.code_tree).parent(argument_first, argument_second)
        elif relation_type == 'PARENTT':
            result_relation = ParentRelation(self.code_tree).parent_t(argument_first, argument_second)
        elif relation_type == 'FOLLOWS':
            result_relation = FollowsRelation(self.code_tree).follows(argument_first, argument_second)
        elif relation_type == 'FOLLOWST':
            result_relation = FollowsRelation(self.code_tree).follows_t(argument_first, argument_second)

        if self.is_and:
            self.result = list(set(self.result).intersection(result_relation))
        else:
            self.result = result_relation
