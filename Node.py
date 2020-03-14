from typing import List
from jsonweb.encode import to_object


@to_object()
class Node:
    def __init__(self, node_type: str = '', value: str = '', line: int = 0) -> None:
        self.children: List[Node] = list()
        self.node_type: str = node_type
        self.value: str = value
        self.line: int = line

    def add_child(self, child) -> None:
        self.children.append(child)

    def to_string(self, i: int) -> None:
        print(str(i) + ": TYPE:" + self.node_type + "\t VALUE:" + self.value + "\t LINE:" + str(self.line))
        for x in self.children:
            x.to_string(i + 1)

    def __repr__(self) -> str:
        return "TYPE:" + self.node_type + "\t VALUE:" + self.value
