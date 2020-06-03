from typing import Set

from aitsi_parser.StatementTable import StatementTable
from pql.Node import Node
from pql.Reference import Reference
from pql.utils.SearchUtils import SearchUtils


class Pattern:

    def __init__(self, ast_node: Node, stmt_table: StatementTable):
        self.search: SearchUtils = SearchUtils(ast_node)
        self.stmt_table: StatementTable = stmt_table

    def execute(self, pattern_node: Node) -> Set[int]:
        if pattern_node.node_type in ['PATTERN_WHILE', 'PATTERN_IF']:
            return self.pattern_while_or_if(pattern_node)
        else:
            return self.pattern_assign(pattern_node)

    def pattern_while_or_if(self, node: Node) -> Set[int]:
        if node.children[1].node_type in ['VARIABLE', 'EVERYTHING']:
            return {Reference(line, '') for line in
                    set(self.stmt_table.get_statement_line_by_type_name(node.children[0].node_type))}
        else:
            return {Reference(line, '') for line in
                    set(self.stmt_table.get_statement_line_by_type_name_and_value(node.children[0].node_type,
                                                                                  node.children[1].value))}

    def pattern_assign(self, node: Node) -> Set[int]:
        if node.children[1].node_type in ['VARIABLE', 'EVERYTHING']:
            result: Set[int] = set(self.stmt_table.get_statement_line_by_type_name(node.children[0].node_type))
        else:  # pobranie wszystkich lini gdy po lewej stronie rownania jest dana wartosć np. "t"
            result: Set[int] = set(self.stmt_table.get_statement_line_by_type_name_and_value(
                node.children[0].node_type, node.children[1].value))

        if result and node.children[2].node_type == "EVERYTHING":
            return self._pattern_assign_check(node.children[2], result, True)
        elif result:
            return self._pattern_assign_check(node.children[2], result, False)

    def _pattern_assign_check(self, node_expr: Node, elements: Set[int], wild_card: bool) -> Set[int]:
        if node_expr.children:
            result: Set[Reference] = set()
            if wild_card:
                for line in elements:
                    search_node: Node = self.search.find_node_by_line(line).children[1]
                    if search_node is not None:
                        if self._expression_part_is_identical(search_node, node_expr.children[0]):
                            result.add(Reference(line, ''))
            else:
                for line in elements:
                    search_node: Node = self.search.find_node_by_line(line).children[1]
                    if search_node is not None:
                        if self._expression_is_identical(search_node, node_expr):
                            result.add(Reference(line, ''))
            return result
        return [Reference(line, '') for line in elements]

    def _expression_part_is_identical(self, ast: Node, comparing_node: Node) -> bool:
        if comparing_node.equals_expression(ast):
            for index, child in enumerate(ast.children):
                if not self._expression_part_is_identical(child, comparing_node.children[index]):
                    return False
            return True
        else:
            for child in ast.children:
                if self._expression_part_is_identical(child, comparing_node):
                    if len(child.children) == 2:
                        return True
                    return True
            return False

    def _expression_is_identical(self, ast: Node, comparing_node: Node) -> bool:
        if comparing_node.equals_expression(ast):
            for index, child in enumerate(ast.children):
                if not self._expression_is_identical(child, comparing_node.children[index]):
                    return False
            return True
        else:
            return False
