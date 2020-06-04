import logging
from typing import List

import dataclasses
from dataclasses import dataclass
from marshmallow.schema import BaseSchema
from marshmallow_dataclass import add_schema

log = logging.getLogger(__name__)


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

    def add_children(self, children_list) -> None:
        self.children.extend(children_list)

    def to_string(self, i: int) -> None:
        print(str(i) + ": TYPE:" + self.node_type + "\t VALUE:" + self.value + "\t LINE:" + str(self.line))
        for x in self.children:
            x.to_string(i + 1)

    def equals_expression(self, other: 'Node') -> bool:
        if self.node_type == other.node_type and self.value == other.value:
            if len(self.children) > len(other.children):
                for child in self.children:
                    if child.node_type == other.children[0].node_type and child.value == other.children[0].value:
                        return True
            elif len(self.children) < len(other.children):
                return False
            elif not other.children:
                return True
            else:
                for index, child in enumerate(self.children):
                    if not child.node_type == other.children[index].node_type \
                            and not child.value == other.children[index].value:
                        return False
            return True
        else:
            return False

    def to_log(self, i: int) -> None:
        log.debug(str(i) + ": TYPE:" + self.node_type + "\t VALUE:" + self.value + "\t LINE:" + str(self.line))
        for x in self.children:
            x.to_log(i + 1)

    def __repr__(self) -> str:
        return "TYPE:" + self.node_type + "\t VALUE:" + self.value

    def __hash__(self):
        return hash(self.value + self.node_type + "".join([node.value + node.node_type for node in self.children]))
