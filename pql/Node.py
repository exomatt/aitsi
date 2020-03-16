from typing import List

import dataclasses
from dataclasses import dataclass
from marshmallow.schema import BaseSchema
from marshmallow_dataclass import add_schema


@dataclass
@add_schema(base_schema=BaseSchema)
class Node:
    node_type: str
    value: str
    line: int
    children: List['Node'] = dataclasses.field(default_factory=lambda: [])

    def __init__(self, node_type: str = '', value: str = '', line: int = 0, children=None) -> None:
        if children is None:
            children = []
        self.children: List[Node] = children
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
