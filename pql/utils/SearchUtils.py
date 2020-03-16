from typing import List, Optional

from pql.Node import Node


class SearchUtils:

    def __init__(self, ast_tree: Node) -> None:
        super().__init__()
        self.ast_tree: Node = ast_tree

    def find_node_by_line(self, line_number: int) -> Optional[Node]:
        s_list: List[Node] = []
        if self.ast_tree.line == line_number:
            return self.ast_tree
        else:
            s_list.extend(self.ast_tree.children)
            while s_list:
                node: Node = s_list.pop()
                if node.line == line_number:
                    return node
                else:
                    s_list.extend(node.children)
        return None

    def find_node_by_line_and_value(self, line_number: int, value: str) -> Optional[Node]:
        s_list: List[Node] = []
        if self.ast_tree.line == line_number and self.ast_tree.value == value:
            return self.ast_tree
        else:
            s_list.extend(self.ast_tree.children)
            while s_list:
                node: Node = s_list.pop()
                if node.line == line_number and node.value == value:
                    return node
                else:
                    s_list.extend(node.children)
        return None
