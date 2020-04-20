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

    def find_node_by_line_and_type_and_value(self, line_number: int, node_type: str, value: str) -> Optional[Node]:
        s_list: List[Node] = []
        if self.ast_tree.line == line_number and self.ast_tree.node_type == node_type and self.ast_tree.value == value:
            return self.ast_tree
        else:
            s_list.extend(self.ast_tree.children)
            while s_list:
                node: Node = s_list.pop()
                if node.line == line_number and node.node_type == node_type and node.value == value:
                    return node
                else:
                    s_list.extend(node.children)
        return None

    def find_node_by_type(self, node_type: str) -> List[Node]:
        results: List[Node] = []
        s_list: List[Node] = []
        if self.ast_tree.node_type == node_type:
            results.append(self.ast_tree)

        s_list.extend(self.ast_tree.children)
        while s_list:
            node: Node = s_list.pop()
            if node.node_type == node_type:
                results.append(node)
            s_list.extend(node.children)

        return results

    def find_node_line_number_by_type(self, node_type: str) -> List[int]:
        results: List[int] = []
        s_list: List[Node] = []
        if self.ast_tree.node_type == node_type:
            results.append(self.ast_tree.line)

        s_list.extend(self.ast_tree.children)
        while s_list:
            node: Node = s_list.pop()
            if node.node_type == node_type:
                results.append(node.line)
            s_list.extend(node.children)

        return results

    def find_last_line_number(self) -> int:
        last_line: int = 0
        while self.find_node_by_line(last_line + 1) is not None:
            last_line += 1
        return last_line
