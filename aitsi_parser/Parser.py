import json
import re
from typing import Tuple, Dict, List

from aitsi_parser.CallsTable import CallsTable
from aitsi_parser.FollowsTable import FollowsTable
from aitsi_parser.ModifiesTable import ModifiesTable
from aitsi_parser.Node import Node
from aitsi_parser.ParentTable import ParentTable
from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.UsesTable import UsesTable
from aitsi_parser.VarTable import VarTable


class Parser:
    token_expressions = [(r"\s*procedure", 'PROCEDURE'), (r"\s*{", "OPEN_BRACKET"), (r"\s*}", "CLOSE_BRACKET"),
                         (r"\s*;", "SEMICOLON"), (r"\s*\+", "PLUS"), (r"\s*\-", "MINUS"), (r"\s*call", "CALL"),
                         (r"\s*while", "WHILE"), (r"\s*\*", "MULTIPLY"), (r"\s*if", "IF"), (r"\s*then", "THEN"),
                         (r"\s*else", "ELSE"), (r"\s*=", "ASSIGN"), (r"\s*\(", "OPEN_PARENTHESIS"),
                         (r"\s*\)", "CLOSE_PARENTHESIS"), (r"\s*[A-Za-z]+[A-Za-z0-9]*", 'NAME'),
                         (r"\s*[0-9]+", 'INTEGER')]

    def __init__(self, code: str, filename: str) -> None:
        self.calls_table: CallsTable = CallsTable()
        self.call_procedure = None
        self.code: str = code.replace('\n', '')
        self.current_line: int = 0
        self.mod_table: ModifiesTable = ModifiesTable()
        self.next_token: Tuple[str, str] = ('', '')  # np.("NAME","x")
        self.parent_table: ParentTable = ParentTable()
        self.follows_table: FollowsTable = FollowsTable()
        self.pos: int = 0
        self.prev_token: Tuple[str, str] = ('', '')  # np.("ASSIGN")
        self.proc_table: ProcTable = ProcTable()
        self.root: Node = Node("PROGRAM", filename)
        self.statement_table: StatementTable = StatementTable()
        self.var_table: VarTable = VarTable()
        self.uses_table: UsesTable = UsesTable()

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
                    new_token = (token, match.group(0).strip())
                    self.pos += len(match.group(0))
                    break
        return new_token

    def error(self) -> None:
        print("ERROR")

    def program(self) -> None:
        self.next_token = self.get_token()
        while self.next_token[0] == "PROCEDURE":
            self.root.add_child(self.procedure())
        for child in self.root.children:
            called_procedures = self.calls_table.get_called_from(child.value)
            for proc in called_procedures:
                modified_vars: List[str] = self.mod_table.get_modified(proc)
                used_vars: List[str] = self.uses_table.get_used(proc)
                for var in modified_vars:
                    self.mod_table.set_modifies(var, child.value)
                for var in used_vars:
                    self.uses_table.set_uses(var, child.value)
        for statement in self.statement_table.table.values:
            if statement[1]['name'] == 'CALL':
                modified_vars: List[str] = self.mod_table.get_modified(statement[1]['value'])
                used_vars: List[str] = self.uses_table.get_used(statement[1]['value'])
                for var in modified_vars:
                    self.mod_table.set_modifies(var, str(statement[0]))
                for var in used_vars:
                    self.uses_table.set_uses(var, str(statement[0]))

    def procedure(self) -> Node:
        self.match("PROCEDURE")
        self.match("NAME")
        proc_node: Node = Node("PROCEDURE", self.prev_token[1])
        self.proc_table.insert_proc(proc_node.value)
        self.call_procedure = proc_node.value
        self.match("OPEN_BRACKET")
        self.proc_table.update_proc(proc_node.value, {'start': self.current_line + 1})
        proc_node.add_child(self.statement_list())
        self.proc_table.update_proc(proc_node.value, {'finish': self.current_line})
        self.match("CLOSE_BRACKET")
        return proc_node

    def statement_list(self) -> Node:
        stmt_list_node: Node = Node("STMT_LIST", self.prev_token[1])
        prev_node: Node = None
        while self.next_token[0] != "CLOSE_BRACKET":
            stmt_node = self.statement()
            if prev_node is not None:
                self.follows_table.set_follows(prev_node.line, stmt_node.line)
            stmt_list_node.add_child(stmt_node)
            prev_node = stmt_node

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
        self.calls_table.set_calls(self.call_procedure, self.next_token[1].strip())
        self.match("NAME")
        call_node: Node = Node("CALL", self.prev_token[1], self.current_line)
        self.statement_table.insert_statement(self.current_line,
                                              {'name': 'CALL', 'value': call_node.value, 'start': self.current_line,
                                               'end': self.current_line})
        self.match("SEMICOLON")
        return call_node

    def while_statement(self) -> Node:
        self.match("WHILE")
        self.match("NAME")
        while_node: Node = Node("WHILE", line=self.current_line)
        while_node.add_child(Node(self.prev_token[0], self.prev_token[1], self.current_line))
        self.uses_table.set_uses(self.prev_token[1], str(self.current_line))
        self.uses_table.set_uses(self.prev_token[1], self.call_procedure)
        self.statement_table.insert_statement(self.current_line, {'name': 'WHILE', 'value': self.prev_token[1],
                                                                  'start': self.current_line})
        self.match("OPEN_BRACKET")
        while_node.add_child(self.statement_list())
        self.statement_table.update_statement(while_node.line, {'end': self.current_line})
        for child in while_node.children[1].children:
            self.parent_table.set_parent(while_node.line, child.line)
            if child.node_type == 'ASSIGN' or child.node_type == 'WHILE' or child.node_type == 'IF':
                for letter in self.mod_table.get_modified(str(child.line)):
                    self.mod_table.set_modifies(letter, str(while_node.line))
                    self.mod_table.set_modifies(letter, self.call_procedure)
                for letter in self.uses_table.get_used(str(child.line)):
                    self.uses_table.set_uses(letter, str(while_node.line))
                    self.uses_table.set_uses(letter, self.call_procedure)
        self.match("CLOSE_BRACKET")

        return while_node

    def assignment(self) -> Node:
        assign_node: Node = Node("ASSIGN", line=self.current_line)
        self.match("NAME")
        assign_node.add_child(Node(self.prev_token[0], self.prev_token[1], self.current_line))
        self.var_table.insert_var(self.prev_token[1])
        self.mod_table.set_modifies(self.prev_token[1], str(self.current_line))
        self.mod_table.set_modifies(self.prev_token[1], self.call_procedure)
        self.statement_table.insert_statement(self.current_line, {'name': 'ASSIGN', 'value': self.prev_token[1],
                                                                  'start': self.current_line, 'end': self.current_line})
        self.match("ASSIGN")
        assign_node.add_child(self.expression())
        self.match("SEMICOLON")

        return assign_node

    def if_statement(self) -> Node:
        if_node: Node = Node("IF", line=self.current_line)
        self.match("IF")
        self.match("NAME")
        if_node.add_child(Node(self.prev_token[0], self.prev_token[1], self.current_line))
        self.statement_table.insert_statement(self.current_line,
                                              {'name': 'IF', 'value': self.prev_token[1], 'start': self.current_line})
        self.uses_table.set_uses(self.prev_token[1], str(self.current_line))
        self.uses_table.set_uses(self.prev_token[1], self.call_procedure)
        self.match("THEN")
        self.match("OPEN_BRACKET")
        if_node.add_child(self.statement_list())
        for child in if_node.children[1].children:
            self.parent_table.set_parent(if_node.line, child.line)
            if child.node_type == 'ASSIGN' or child.node_type == 'WHILE' or child.node_type == 'IF':
                for letter in self.mod_table.get_modified(str(child.line)):
                    self.mod_table.set_modifies(letter, str(if_node.line))
                    self.mod_table.set_modifies(letter, self.call_procedure)
                for letter in self.uses_table.get_used(str(child.line)):
                    self.uses_table.set_uses(letter, str(if_node.line))
                    self.uses_table.set_uses(letter, self.call_procedure)
        self.match("CLOSE_BRACKET")
        self.match("ELSE")
        self.match("OPEN_BRACKET")
        if_node.add_child(self.statement_list())
        for child in if_node.children[2].children:
            self.parent_table.set_parent(if_node.line, child.line)
            if child.node_type == 'ASSIGN' or child.node_type == 'WHILE' or child.node_type == 'IF':
                for letter in self.mod_table.get_modified(str(child.line)):
                    self.mod_table.set_modifies(letter, str(if_node.line))
                    self.mod_table.set_modifies(letter, self.call_procedure)
                for letter in self.uses_table.get_used(str(child.line)):
                    self.uses_table.set_uses(letter, str(if_node.line))
                    self.uses_table.set_uses(letter, self.call_procedure)
        self.match("CLOSE_BRACKET")
        self.statement_table.update_statement(if_node.line, {'end': self.current_line})
        return if_node

    def expression(self) -> Node:
        node: Node = self.term()
        while self.next_token[0] in ["PLUS", "MINUS"]:
            op_node: Node = Node(self.next_token[0], line=self.current_line)
            self.match(self.next_token[0])
            op_node.add_child(node)
            op_node.add_child(self.term())
            node = op_node
        return node

    def term(self) -> Node:
        node: Node = self.factor()
        while self.next_token[0] == "MULTIPLY":
            multiply_node: Node = Node(self.next_token[0], self.next_token[1], self.current_line)
            self.match("MULTIPLY")
            multiply_node.add_child(node)
            multiply_node.add_child(self.factor())
            node = multiply_node
        return node

    def factor(self) -> Node:
        if self.next_token[0] == "OPEN_PARENTHESIS":
            self.match("OPEN_PARENTHESIS")
            factor_node: Node = self.expression()
            self.match("CLOSE_PARENTHESIS")
            return factor_node
        elif self.next_token[0] == "INTEGER":
            self.match("INTEGER")
            return Node(self.prev_token[0], self.prev_token[1], self.current_line)
        elif self.next_token[0] == "NAME":
            self.match("NAME")
            self.uses_table.set_uses(self.prev_token[1], str(self.current_line))
            self.uses_table.set_uses(self.prev_token[1], self.call_procedure)
            return Node(self.prev_token[0], self.prev_token[1], self.current_line)

    def get_node_json(self) -> Dict[str, dict]:
        json_str = Node.Schema().dumps(self.root)
        json_dict: Dict[str, dict] = json.loads(json_str)
        return json_dict
