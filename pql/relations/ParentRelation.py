from typing import Optional, List, Union

from pql.Node import Node
from pql.utils.SearchUtils import SearchUtils


class ParentRelation:

    def __init__(self, ast_tree: Node) -> None:
        super().__init__()
        self.ast_tree: Node = ast_tree

    def parent(self, param_first: str, param_second: str, ) -> Union[bool, List[int]]:
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        if param_first.isdigit():
            if param_second.isdigit():
                # p1 i p2 sa liczbami
                node: Optional[Node] = search_utils.find_node_by_line(int(param_first))
                if node is None:
                    return False
                elif node.node_type in ['IF', 'WHILE']:
                    stmt_list: List[Node] = []
                    for children in node.children:
                        if children.node_type == 'STMT_LIST':
                            stmt_list.extend(children.children)
                    for stmt in stmt_list:
                        if stmt.line == int(param_second):
                            return True
                return False
            else:
                # p1 jest liczba, a p2 nie
                node: Optional[Node] = search_utils.find_node_by_line(int(param_first))
                if node is None:
                    return []
                elif node.node_type in ['IF', 'WHILE']:
                    if param_second == '_':
                        stmt_list: List[Node] = []
                        result_lines: List[int] = []
                        for children in node.children:
                            if children.node_type == 'STMT_LIST':
                                stmt_list.extend(children.children)
                        for stmt in stmt_list:
                            if stmt.line != 0:
                                result_lines.append(stmt.line)
                        return result_lines
                    else:
                        stmt_list: List[Node] = []
                        result_lines: List[int] = []
                        for children in node.children:
                            if children.node_type == 'STMT_LIST':
                                stmt_list.extend(children.children)
                        for stmt in stmt_list:
                            if stmt.node_type == param_second:
                                result_lines.append(stmt.line)
                        return result_lines
                return []
        else:
            if param_second.isdigit():
                # p1 nie jest liczba, a p2 jest liczba
                if param_first == '_':
                    nodes_by_type: List[Node] = []
                    nodes_by_type.extend(search_utils.find_node_by_type('WHILE'))
                    nodes_by_type.extend(search_utils.find_node_by_type('IF'))
                    return self._check_if_nodes_contain_line(nodes_by_type, param_second)
                elif param_first in ['IF', 'WHILE']:
                    nodes_by_type: List[Node] = search_utils.find_node_by_type(param_first)
                    return self._check_if_nodes_contain_line(nodes_by_type, param_second)
                else:
                    return False
            else:
                # p1 i p2 nie sa liczbami
                if param_first == '_' and param_second == '_':
                    nodes_by_type: List[Node] = []
                    nodes_by_type.extend(search_utils.find_node_by_type('WHILE'))
                    nodes_by_type.extend(search_utils.find_node_by_type('IF'))
                    stmt_list: List[Node] = []
                    result_lines: List[int] = []
                    for node in nodes_by_type:
                        for children in node.children:
                            if children.node_type == 'STMT_LIST':
                                stmt_list.extend(children.children)
                    for stmt in stmt_list:
                        if stmt.line != 0:
                            result_lines.append(stmt.line)
                    return result_lines
                elif param_first == '_':
                    nodes_by_type: List[Node] = []
                    nodes_by_type.extend(search_utils.find_node_by_type('WHILE'))
                    nodes_by_type.extend(search_utils.find_node_by_type('IF'))
                    stmt_list: List[Node] = []
                    result_lines: List[int] = []
                    for node in nodes_by_type:
                        for children in node.children:
                            if children.node_type == 'STMT_LIST':
                                stmt_list.extend(children.children)
                    for stmt in stmt_list:
                        if stmt.node_type == param_second:
                            result_lines.append(stmt.line)
                    return result_lines
                elif param_first in ['IF', 'WHILE']:
                    nodes_by_type: List[Node] = search_utils.find_node_by_type(param_first)
                    if param_second == '_':
                        stmt_list: List[Node] = []
                        result_lines: List[int] = []
                        for node in nodes_by_type:
                            for children in node.children:
                                if children.node_type == 'STMT_LIST':
                                    stmt_list.extend(children.children)
                        for stmt in stmt_list:
                            if stmt.line != 0:
                                result_lines.append(stmt.line)
                        return result_lines
                    else:
                        stmt_list: List[Node] = []
                        result_lines: List[int] = []
                        for node in nodes_by_type:
                            for children in node.children:
                                if children.node_type == 'STMT_LIST':
                                    stmt_list.extend(children.children)
                        for stmt in stmt_list:
                            if stmt.node_type == param_second:
                                result_lines.append(stmt.line)
                        return result_lines
                else:
                    return False

    def _check_if_nodes_contain_line(self, nodes_by_type, param_second) -> bool:
        stmt_list: List[Node] = []
        for node in nodes_by_type:
            for children in node.children:
                if children.node_type == 'STMT_LIST':
                    stmt_list.extend(children.children)
        for stmt in stmt_list:
            if stmt.line == int(param_second):
                return True
        return False

    def parent_T(self, param_first: str, param_second: str) -> bool:
        pass
