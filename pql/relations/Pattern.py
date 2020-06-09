from typing import Set, Tuple, Union

from aitsi_parser.StatementTable import StatementTable
from pql.Node import Node
from pql.utils.SearchUtils import SearchUtils


class Pattern:

    def __init__(self, ast_node: Node, stmt_table: StatementTable):
        self.search: SearchUtils = SearchUtils(ast_node)
        self.stmt_table: StatementTable = stmt_table
        self.node_expr: Node = Node()

    def execute(self, pattern_node: Node, result_operator: Union[Set[int], None],
                result_variable: Union[Set[str], None]) -> Tuple[
        Union[Set[int], Set[str]], Union[Set[int], Set[str], None]]:
        if pattern_node.node_type in ['PATTERN_WHILE', 'PATTERN_IF']:
            return self.pattern_while_or_if(pattern_node, result_operator, result_variable)
        else:
            return self.pattern_assign(pattern_node, result_operator, result_variable)

    def pattern_while_or_if(self, node: Node, result_operator: Union[Set[int], None],
                            result_variable: Union[Set[str], None]) -> Tuple[
        Union[Set[int], Set[str]], Union[Set[int], Set[str], None]]:
        if node.children[1].node_type == 'VARIABLE':
            if result_operator:
                result_line: Set[int] = set(self.stmt_table.get_statement_line_by_type_name(node.children[0].node_type)).intersection(result_operator)
            else:
                result_line: Set[int] = set(self.stmt_table.get_statement_line_by_type_name(node.children[0].node_type))
            result_name: Set[str] = {self.stmt_table.get_other_info(line)['value'] for line in result_line}
            if result_variable:
                result_name = result_name.intersection(result_variable)
                if result_operator:
                    result_line = {line for line in result_line if self.stmt_table.get_other_info(line)['value'] in result_name}.intersection(result_operator)
                else:
                    result_line = {line for line in result_line if self.stmt_table.get_other_info(line)['value'] in result_name}
            return result_line, result_name
        elif node.children[1].node_type == 'EVERYTHING':
            return set(self.stmt_table.get_statement_line_by_type_name(node.children[0].node_type)), None
        else:
            return set(self.stmt_table.get_statement_line_by_type_name_and_value(node.children[0].node_type,
                                                                                 node.children[1].value)), None

    def pattern_assign(self, node: Node, result_operator: Union[Set[int], None],
                       result_variable: Union[Set[str], None]) -> Tuple[
        Union[Set[int], Set[str]], Union[Set[int], Set[str], None]]:
        if node.children[1].node_type in ['VARIABLE', 'EVERYTHING']:
            result: Set[int] = set(self.stmt_table.get_statement_line_by_type_name(node.children[0].node_type))
        else:  # pobranie wszystkich lini gdy po lewej stronie rownania jest dana wartosć np. "t"
            result: Set[int] = set(self.stmt_table.get_statement_line_by_type_name_and_value(
                node.children[0].node_type, node.children[1].value))

        if node.children[2].children:
            self.node_expr = node.children[2].children[0]
        result_line: Set[int] = set()
        if result and node.children[2].node_type == "EVERYTHING":
            result_line = self._pattern_assign_check(node.children[2], result, True)
        elif result:
            result_line = self._pattern_assign_check(node.children[2], result, False)

        if node.children[1].node_type == 'VARIABLE':
            if result_operator:
                result_line: Set[int] = result_line.intersection(result_operator)
            result_name: Set[str] = {self.stmt_table.get_other_info(line)['value'] for line in result_line}
            if result_variable:
                result_name = result_name.intersection(result_variable)
                if result_operator:
                    result_line = {line for line in result_line if self.stmt_table.get_other_info(line)['value'] in result_name}.intersection(result_operator)
                else:
                    result_line = {line for line in result_line if self.stmt_table.get_other_info(line)['value'] in result_name}
            return result_line, result_name
        else:
            return result_line, {self.stmt_table.get_other_info(line)['value'] for line in result_line}

    def _pattern_assign_check(self, node_expr: Node, elements: Set[int], wild_card: bool) -> Set[int]:
        if node_expr.children:
            result: Set[int] = set()
            if wild_card:
                for line in elements:
                    search_node: Node = self.search.find_node_by_line(line).children[1]
                    if search_node is not None:
                        if self._expression_part_is_identical(search_node, node_expr.children[0]):
                            result.add(int(line))
            else:
                for line in elements:
                    search_node: Node = self.search.find_node_by_line(line).children[1]
                    if search_node is not None:
                        if self._expression_is_identical(search_node, node_expr):
                            result.add(int(line))
            return result
        return elements

    def _expression_part_is_identical(self, ast: Node, comparing_node: Node) -> bool:
        if comparing_node.equals_expression(ast):
            for index, child in enumerate(ast.children):
                if not self._expression_part_is_identical(child, comparing_node.children[index]):
                    return False
            return True
        else:
            for child in ast.children:
                if self._expression_part_is_identical(child, self.node_expr):
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
