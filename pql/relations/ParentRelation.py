from typing import Optional, List, Union

from pql.Node import Node
from pql.utils.SearchUtils import SearchUtils


class ParentRelation:

    def __init__(self, ast_tree: Node) -> None:
        super().__init__()
        self.ast_tree: Node = ast_tree

    def parent(self, param_first: str, param_second: str) -> Union[bool, List[int]]:
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
                pass
                # p1 nie jest liczba, a p2 jest liczba

            else:
                # p1 i p2 nie sa liczbami
                # if p1 i p2 sa w tej samej stmt_lst
                # if p1 i p2 maja odpowiedni rodzaj
                # linia p1+1 = linia p2
                pass

    def parent_T(self, param_first: str, param_second: str) -> bool:
        pass
