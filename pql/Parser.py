import json
import re
from typing import Tuple, Dict

from pql.Node import Node


class Parser:
    # znacznik * jest przekształcony na litere T(np. Follows* == FOLLOWST)
    token_expressions = [(r'\s*Select', 'SELECT'), (r'\s*such that', 'SUCH_THAT'),
                         (r'\s*Follows|\s*Follows*|\s*Parent|\s*Parent*|\s*Uses|\s*Uses*|\s*Modifies|\s*Modifies*|'
                          r'\s*Calls|\s*Calls*', 'REL_REF'),
                         (r"\s*Follows", 'FOLLOWS'), (r'\s*Parent', 'PARENT'), (r'\s*Modifies', 'MODIFIES'),
                         (r'\s*Uses', 'USES'), (r'\s*CallS', 'CALLS'),
                         (r'\s*Follows*', 'FOLLOWST'), (r'\s*Parent*', 'PARENTT'), (r'\s*Modifies*', 'MODIFIEST'),
                         (r'\s*Uses*', 'USEST'), (r'\s*CallS*', 'CALLST'),
                         (r'\s*\(', 'OPEN_PARENTHESIS'), (r'\s*\)', 'CLOSE_PARENTHESIS'), (r'\s*;', 'SEMICOLON'),
                         (r"\s*=", "EQUALS_SIGN"),
                         (r'\s*_', 'EVERYTHING'), (r'\s*"', 'QUOTE'),
                         (r'\s*while|\s*assign|\s*stmt|\s*variable|\s*constant|\s*prog_line', 'DECLARATION'),
                         (r'\s*if', 'IF'), (r'\s*while', 'WHILE'), (r'\s*assign', 'ASSIGN'),
                         (r'\s*procedure', 'PROCEDURE'), (r'\s*call', 'CALL'), (r'\s*stmt', 'STMT'),
                         (r'\s*variable', 'VARIABLE'), (r'\s*BOOLEAN', 'BOOLEAN'), (r'\s*constant', 'CONSTANT'),
                         (r'\s*prog_line', 'PROG_LINE'),
                         (r'\s*with', 'WITH'), (r'\s*and', 'AND'),
                         (r'\s*[A-Za-z]+[A-Za-z0-9#]*', 'IDENT'),
                         (r'\s*[0-9]+', 'INTEGER'), (r'\s*,', 'COMMA')]

    def __init__(self) -> None:
        # todo inicjalizacja

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
                    new_token = (token, match.group(0))
                    self.pos += len(match.group(0))
                    break
        return new_token

    def parse(self, query: str) -> None:
        self.query: str = query.replace('\n', '')
        self.next_token = self.get_token()
        self.root.add_child(self.select_cl())
        self.root.to_string(0)

    def stmt_ref(self) -> Node:
        if self.next_token[0] == "IDENT":
            self.synonym()
        elif self.next_token[0] == "EVERYTHING":
            self.match("EVERYTHING")
        elif self.next_token[0] == "INTEGER":
            self.match("INTEGER")
        return Node("STMT_REF", self.prev_token[1])

    def ent_ref(self) -> Node:
        if self.next_token[0] == "IDENT":
            self.synonym()
        elif self.next_token[0] == "EVERYTHING":
            self.match("EVERYTHING")
        elif self.next_token[0] == "":
            self.match("")
        return Node("ENT_REF", self.prev_token[1])

    def select_cl(self) -> Node:
        # declaration
        self.root.add_child(self.design_entity())
        self.match("SELECT")
        self.synonym()
        if self.next_token[0] == "SUCH_THAT":
            return self.such_that_cl()
        elif self.next_token[0] == "WITH":
            return self.with_cl()

    def declaration(self) -> Node:
        declaration_list_node: Node = Node(self.prev_token[1].upper())
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
        such_that_node: Node = Node("SUCH_THAT", "")
        # such_that_node.add_child(self.rel_ref())
        return such_that_node

    def rel_ref(self) -> Node:
        if self.next_token[0] == "MODIFIES":
            return self.modifies()
        elif self.next_token[0] == "USES":
            return self.uses()
        elif self.next_token[0] == "PARENT":
            return self.parent()
        elif self.next_token[0] == "PARENTT":
            return self.parent_t()
        elif self.next_token[0] == "FOLLOWS":
            return self.follows()
        elif self.next_token[0] == "FOLLOWST":
            return self.follows_t()
        # self.match("REL_REF")
        # rel_ref_node: Node = Node(self.prev_token[1].upper())
        # while self.next_token[0] != "CLOSE_PARENTHESIS":
        #     self.match("OPEN_PARENTHESIS")
        #     rel_ref_node.add_child()
        #     declaration_node.add_child(self.declaration())
        # return declaration_node

    def modifies(self) -> Node:
        self.match("MODIFIES")
        modifies_node: Node = Node("MODIFIES")
        while self.next_token[0] != "CLOSE_PARENTHESIS":
            self.match("OPEN_PARENTHESIS")
            modifies_node.add_child(self.stmt_ref())
            if self.next_token[0] == "COMMA":
                self.match("COMMA")
                modifies_node.add_child(self.ent_ref())
                self.match("CLOSE_PARENTHESIS")
        return modifies_node

    def modifies_t(self) -> Node:
        pass

    def uses(self) -> Node:
        pass

    def uses_t(self) -> Node:
        pass

    def parent(self) -> Node:
        pass

    def parent_t(self) -> Node:
        pass

    def follows(self) -> Node:
        pass

    def follows_t(self) -> Node:
        pass

    def with_cl(self) -> Node:
        pass

    def ref(self) -> Node:
        pass

    def synonym(self):
        self.match("IDENT")

    def get_node_json(self) -> Dict[str, dict]:
        json_str = Node.Schema().dumps(self.root)
        json_dict: Dict[str, dict] = json.loads(json_str)
        return json_dict
