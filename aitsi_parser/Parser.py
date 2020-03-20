import json
import re
from typing import Tuple, Dict

from aitsi_parser.ModifiesTable import ModifiesTable
from aitsi_parser.Node import Node
from aitsi_parser.ParentTable import ParentTable
from aitsi_parser.VarTable import VarTable


class Parser:
    token_expressions = [(r"\s*procedure", 'PROCEDURE'), (r"\s*{", "OPEN_BRACKET"), (r"\s*}", "CLOSE_BRACKET"),
                         (r"\s*;", "SEMICOLON"), (r"\s*\+", "PLUS"), (r"\s*\-", "MINUS"), (r"\s*call", "CALL"),
                         (r"\s*while", "WHILE"), (r"\s*\*", "MULTIPLY"), (r"\s*if", "IF"), (r"\s*then", "THEN"),
                         (r"\s*else", "ELSE"), (r"\s*=", "ASSIGN"), (r"\s*\(", "OPEN_PARENTHESIS"),
                         (r"\s*\)", "CLOSE_PARENTHESIS"), (r"\s*[A-Za-z]+[A-Za-z0-9]*", 'NAME'),
                         (r"\s*[0-9]+", 'INTEGER')]

    def __init__(self, code: str) -> None:
        self.code: str = code.replace('\n', '')
        self.current_line: int = 0
        self.mod_table: ModifiesTable = ModifiesTable()
        self.next_token: Tuple[str, str] = ('', '')  # np.("NAME","x")
        self.parent_table: ParentTable = ParentTable()
        self.pos: int = 0
        self.prev_token: Tuple[str, str] = ('', '')  # np.("ASSIGN")
        self.root: Node = Node("PROGRAM", "program")
        self.var_table: VarTable = VarTable()

    def match(self, token: str) -> None:
        if self.next_token[0] == token:
            self.prev_token = self.next_token
            self.next_token = self.get_token()
        else:
            self.error()

    def get_token(self) -> Tuple[str, str]:
        new_token: Tuple[str, str] = ('', '')
        code: str = self.code
        for exp, token in self.token_expressions:
            regex = re.compile(exp)
            match = regex.match(code, self.pos)
            if match is not None:
                if match.group(0):
                    new_token = (token, match.group(0))
                    self.pos += len(match.group(0))
                    break
        return new_token

    def error(self) -> None:
        print("ERROR")

    def program(self) -> None:
        self.next_token = self.get_token()
        self.root.add_child(self.procedure())

    def procedure(self) -> Node:
        self.match("PROCEDURE")
        self.match("NAME")
        proc_node: Node = Node("PROCEDURE", self.prev_token[1])
        self.match("OPEN_BRACKET")
        proc_node.add_child(self.statement_list())
        self.match("CLOSE_BRACKET")
        return proc_node

    def statement_list(self) -> Node:
        stmt_list_node: Node = Node("STMT_LIST", self.prev_token[1])
        while self.next_token[0] != "CLOSE_BRACKET":
            stmt_list_node.add_child(self.statement())

        return stmt_list_node

    def statement(self) -> Node:
        self.current_line += 1
        if self.next_token[0] == "WHILE":
            return self.while_statement()
        elif self.next_token[0] == "CALL":
            return self.call()
        elif self.next_token[0] == "IF":
            return self.if_statement()
        else:
            return self.assignment()

    def call(self) -> Node:
        self.match("CALL")
        self.match("NAME")
        call_node: Node = Node("CALL", self.prev_token[1], self.current_line)
        self.match("SEMICOLON")
        return call_node

    def while_statement(self) -> Node:
        self.match("WHILE")
        self.match("NAME")
        while_node: Node = Node("WHILE", line=self.current_line)
        while_node.add_child(Node(self.prev_token[0], self.prev_token[1], self.current_line))
        self.match("OPEN_BRACKET")
        while_node.add_child(self.statement_list())
        for child in while_node.children[1].children:
            self.parent_table.set_parent(while_node.line, child.line)
            if child.node_type == 'ASSIGN':
                for letter in self.mod_table.get_modified(child.line):
                    self.mod_table.set_modifies(letter, while_node.line)
        self.match("CLOSE_BRACKET")

        return while_node

    def assignment(self) -> Node:
        assign_node: Node = Node("ASSIGN", line=self.current_line)
        self.match("NAME")
        assign_node.add_child(Node(self.prev_token[0], self.prev_token[1], self.current_line))
        self.var_table.insert_var(self.prev_token[1])
        self.mod_table.set_modifies(self.prev_token[1], self.current_line)
        self.match("ASSIGN")
        assign_node.add_child(self.expression())
        self.match("SEMICOLON")

        return assign_node

    def if_statement(self) -> Node:
        if_node: Node = Node("IF", line=self.current_line)
        self.match("IF")
        self.match("NAME")
        if_node.add_child(Node(self.prev_token[0], self.prev_token[1], self.current_line))
        self.match("THEN")
        self.match("OPEN_BRACKET")
        if_node.add_child(self.statement_list())
        for child in if_node.children[1].children:
            self.parent_table.set_parent(if_node.line, child.line)
            if child.node_type == 'ASSIGN':
                for letter in self.mod_table.get_modified(child.line):
                    self.mod_table.set_modifies(letter, if_node.line)
        self.match("CLOSE_BRACKET")
        self.match("ELSE")
        self.match("OPEN_BRACKET")
        if_node.add_child(self.statement_list())
        for child in if_node.children[2].children:
            self.parent_table.set_parent(if_node.line, child.line)
            if child.node_type == 'ASSIGN':
                for letter in self.mod_table.get_modified(child.line):
                    self.mod_table.set_modifies(letter, if_node.line)
        self.match("CLOSE_BRACKET")

        return if_node

    def expression(self) -> Node:
        if self.next_token[0] == "NAME":
            self.match("NAME")
        elif self.next_token[0] == "INTEGER":
            self.match("INTEGER")
        left: Node = Node(self.prev_token[0], self.prev_token[1], self.current_line)
        if self.next_token[0] != "SEMICOLON":
            op_node: Node = Node(self.next_token[0], line=self.current_line)
            op_node.add_child(left)
            self.match(self.next_token[0])
            op_node.add_child(self.expression())
        else:
            return left
        return op_node

    def get_node_json(self) -> Dict[str, dict]:
        json_str = Node.Schema().dumps(self.root)
        json_dict: Dict[str, dict] = json.loads(json_str)
        return json_dict
