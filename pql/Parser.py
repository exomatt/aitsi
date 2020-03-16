import re
from typing import Tuple

from pql.Node import Node


class Parser:
    # znacznik * jest przekształcony na litere T(np. Follows* == FOLLOWST)
    token_expressions = [(r'\s*Select', 'SELECT'), (r'\s*such that', 'SUCH_THAT'),
                         (r'\s*Follows\*', 'FOLLOWST'), (r'\s*Parent\*', 'PARENTT'), (r'\s*Modifies\*', 'MODIFIEST'),
                         (r'\s*Uses\*', 'USEST'), (r'\s*CallS\*', 'CALLST'),
                         (r"\s*Follows", 'FOLLOWS'), (r'\s*Parent', 'PARENT'), (r'\s*Modifies', 'MODIFIES'),
                         (r'\s*Uses', 'USES'), (r'\s*CallS', 'CALLS'),
                         (r'\s*\(', 'OPEN_PARENTHESIS'), (r'\s*\)', 'CLOSE_PARENTHESIS'), (r'\s*;', 'SEMICOLON'),
                         (r"\s*=", "EQUALS_SIGN"),
                         (r'\s*_', 'EVERYTHING'), (r'\s*"', 'QUOTE'),
                         (r'\s*while|\s*assign|\s*stmt|\s*variable|\s*constant|\s*prog_line', 'DECLARATION'),
                         (r'\s*BOOLEAN', 'BOOLEAN'),
                         (r'\s*with', 'WITH'), (r'\s*and', 'AND'),
                         (r'\s*"[A-Za-z]+[A-Za-z0-9#]*"', 'IDENT_QUOTE'), (r'\s*[A-Za-z]+[A-Za-z0-9\#]*', 'IDENT'),
                         (r'\s*[0-9]+', 'INTEGER'), (r'\s*,', 'COMMA'), (r'\s*\.', 'DOT')]

    def __init__(self) -> None:
        self.pos: int = 0
        self.prev_token: Tuple[str, str] = ('', '')
        self.next_token: Tuple[str, str] = ('', '')
        self.root: Node = Node("QUERY", "query")

    def match(self, token: str) -> None:
        if self.next_token[0] == token:
            self.prev_token = self.next_token
            self.next_token = self.get_token()
        else:
            self.error()

    def error(self) -> None:
        print("ERROR")

    def get_token(self) -> Tuple[str, str]:
        new_token: Tuple[str, str] = ('', '')
        query: str = self.query
        for exp, token in self.token_expressions:
            regex = re.compile(exp)
            match = regex.match(query, self.pos)
            if match is not None:
                if match.group(0):
                    if self.prev_token[0] != "DOT":
                        new_token = (token, match.group(0))
                        self.pos += len(match.group(0))
                        break
                    elif token == "IDENT":
                        new_token = (token, match.group(0))
                        self.pos += len(match.group(0))
                        break

        return new_token

    def parse(self, query: str) -> None:
        self.query: str = query.replace('\n', '')
        self.next_token = self.get_token()
        self.select_cl()
        self.root.to_string(0)

    def stmt_ref(self) -> Node:
        if self.next_token[0] == "IDENT":
            self.synonym()
        elif self.next_token[0] == "EVERYTHING":
            self.match("EVERYTHING")
        elif self.next_token[0] == "INTEGER":
            self.match("INTEGER")
        return Node(self.prev_token[0], self.prev_token[1])

    def ent_ref(self) -> Node:
        if self.next_token[0] == "IDENT":
            self.synonym()
        elif self.next_token[0] == "EVERYTHING":
            self.match("EVERYTHING")
        elif self.next_token[0] == "QUOTE":
            self.match("IDENT_QUOTE")

        return Node(self.prev_token[0], self.prev_token[1])

    def select_cl(self) -> None:
        self.root.add_child(self.design_entity())
        self.match("SELECT")
        result_node: Node = Node("RESULT")
        self.synonym()
        result_node.add_child(Node(self.prev_token[0], self.prev_token[1]))
        self.root.add_child(result_node)
        if self.next_token[0] == "SUCH_THAT":
            self.root.add_child(self.such_that_cl())
        if self.next_token[0] == "WITH":
            self.root.add_child(self.with_cl())

    def declaration(self) -> Node:
        declaration_list_node: Node = Node(self.prev_token[1].upper().strip())
        while self.next_token[0] != "SEMICOLON":
            self.synonym()
            declaration_list_node.add_child(Node("SYNONYM", self.prev_token[1]))
            if self.next_token[0] == "COMMA":
                self.match("COMMA")
        self.match("SEMICOLON")

        return declaration_list_node

    def design_entity(self) -> Node:
        declaration_node: Node = Node("DECLARATION")
        while self.next_token[0] != "SELECT":
            if self.next_token[0] == "DECLARATION":
                self.match("DECLARATION")
                declaration_node.add_child(self.declaration())
        return declaration_node

    def such_that_cl(self) -> Node:
        self.match("SUCH_THAT")
        such_that_node: Node = Node("SUCH_THAT")
        such_that_node.add_child(self.rel_ref())
        return such_that_node

    def rel_ref(self) -> Node:
        if self.next_token[0] == "MODIFIES":
            return self.relation_with_other_arguments("MODIFIES")
        elif self.next_token[0] == "MODIFIEST":
            return self.relation_with_other_arguments("MODIFIEST")
        elif self.next_token[0] == "USES":
            return self.relation_with_other_arguments("USES")
        elif self.next_token[0] == "USEST":
            return self.relation_with_other_arguments("USEST")
        elif self.next_token[0] == "PARENT":
            return self.relation_with_the_same_arguments("PARENT")
        elif self.next_token[0] == "PARENTT":
            return self.relation_with_the_same_arguments("PARENTT")
        elif self.next_token[0] == "FOLLOWS":
            return self.relation_with_the_same_arguments("FOLLOWS")
        elif self.next_token[0] == "FOLLOWST":
            return self.relation_with_the_same_arguments("FOLLOWST")

    def relation_with_the_same_arguments(self, type_node: str) -> Node:
        self.match(type_node)
        relation_node: Node = Node(type_node)
        self.match("OPEN_PARENTHESIS")
        relation_node.add_child(self.stmt_ref())
        self.match("COMMA")
        relation_node.add_child(self.stmt_ref())
        self.match("CLOSE_PARENTHESIS")
        if self.next_token[0] == "AND":
            self.match("AND")
            relation_node.add_child(self.rel_ref())
        return relation_node

    def relation_with_other_arguments(self, type_node: str) -> Node:
        self.match(type_node)
        relation_node: Node = Node(type_node)
        self.match("OPEN_PARENTHESIS")
        relation_node.add_child(self.stmt_ref())
        self.match("COMMA")
        relation_node.add_child(self.ent_ref())
        self.match("CLOSE_PARENTHESIS")
        if self.next_token[0] == "AND":
            self.match("AND")
            relation_node.add_child(self.rel_ref())
        return relation_node

    def with_cl(self) -> Node:
        self.match("WITH")
        with_node: Node = Node("WITH")
        with_node.add_child(self.attribute())
        return with_node

    def attribute(self) -> Node:
        self.synonym()
        synonym_node: Node = Node(self.prev_token[0], self.prev_token[1])
        synonym_node.add_child(self.attr_name())
        if self.next_token[0] == "AND":
            self.match("AND")
            synonym_node.add_child(self.attribute())
        return synonym_node

    def attr_name(self) -> Node:
        self.match("DOT")
        self.match("IDENT")
        attr_name_node: Node = Node("ATTR_NAME", self.prev_token[1])
        attr_name_node.add_child(self.ref())
        return attr_name_node

    def attribute_value(self) -> Node:
        self.synonym()
        synonym_node: Node = Node(self.prev_token[0], self.prev_token[1])
        synonym_node.add_child(self.attr_name_value())
        return synonym_node

    def attr_name_value(self) -> Node:
        self.match("DOT")
        self.match("IDENT")
        attr_name_node: Node = Node("ATTR_NAME", self.prev_token[1])
        return attr_name_node

    def ref(self) -> Node:
        self.match("EQUALS_SIGN")
        ref_node: Node = Node(self.next_token[0], self.next_token[1])
        if self.next_token[0] == "IDENT_QUOTE":
            self.match("IDENT_QUOTE")
        elif self.next_token[0] == "INTEGER":
            self.match("INTEGER")
        elif self.next_token[0] == "IDENT":
            return self.attribute_value()
        return ref_node

    def synonym(self):
        self.match("IDENT")
