import json
import re
from typing import Tuple, Dict, List, Set

from aitsi_parser.Node import Node


class Parser:
    token_expressions = [(r"\s*procedure", 'PROCEDURE', 'procedure'), (r"\s*{", "OPEN_BRACKET", '{'),
                         (r"\s*}", "CLOSE_BRACKET", '}'),
                         (r"\s*;", "SEMICOLON", ';'), (r"\s*\+", "PLUS", '+'), (r"\s*\-", "MINUS", '-'),
                         (r"\s*call", "CALL", 'call'),
                         (r"\s*while", "WHILE", 'while'), (r"\s*\*", "MULTIPLY", '*'), (r"\s*if", "IF", 'if'),
                         (r"\s*then", "THEN", 'then'),
                         (r"\s*else", "ELSE", 'else'), (r"\s*=", "ASSIGN", '='), (r"\s*\(", "OPEN_PARENTHESIS", '('),
                         (r"\s*\)", "CLOSE_PARENTHESIS", ')'), (r"\s*[A-Za-z]+[A-Za-z0-9]*", 'NAME', 'name'),
                         (r"\s*[0-9]+", 'INTEGER', 'integer')]

    def __init__(self, code: str, filename: str) -> None:
        self.calls_table: Dict = {}
        self.const_table: Dict = {}
        self.mod_table: Dict = {}
        self.next_table: Dict = {}
        self.parent_table: Dict = {}
        self.follows_table: Dict = {}
        self.proc_table: List = []
        self.statement_table: List = []
        self.var_table: Set = set()
        self.uses_table: Dict = {}
        self.call_procedure = None
        self.code: str = code.replace('\n', '')
        self.current_line: int = 0
        self.next_token: Tuple[str, str] = ('', '')  # np.("NAME","x")
        self.pos: int = 0
        self.prev_token: Tuple[str, str] = ('', '')  # np.("ASSIGN")
        self.root: Node = Node("PROGRAM", filename)

    def match(self, token: str) -> None:
        try:
            if self.next_token[0] == token:
                self.prev_token = self.next_token
                self.next_token = self.get_token()
            else:
                self.throw_exception(token)
                raise Exception
        except:
            log.exception("SyntaxWhileParsingError")
            raise Exception("Check logs for more info")

    def throw_exception(self, token):
        for x in self.token_expressions:
            if x[1] == token and (self.next_token[0] == 'NAME' or self.next_token[0] == 'INTEGER'):
                raise Exception(
                    f"Line {self.current_line}: Expected '{x[2]}' but received '{self.next_token[1]}' instead.")
            elif x[1] == token and (
                    self.prev_token[0] == 'IF' or self.prev_token[0] == 'WHILE' or self.next_token[0] == 'ASSIGN'):
                raise Exception(
                    f"Line {self.current_line}: Expected a variable name but received '{self.next_token[2]}' instead.")
            elif x[1] == token:
                raise Exception(
                    f"Line {self.current_line}: Expected '{x[2]}' but received '{self.next_token[2]}' instead.")

    def get_token(self) -> Tuple[str, str, str]:
        new_token: Tuple[str, str, str] = ('', '', '')
        code: str = self.code
        for exp, token, error in self.token_expressions:
            regex = re.compile(exp)
            match = regex.match(code, self.pos)
            if match is not None:
                if match.group(0):
                    new_token = (token, match.group(0).strip(), error)
                    self.pos += len(match.group(0))
                    break
        return new_token

    def error(self, info: str) -> None:
        log.error("ERROR: " + info)

    def program(self) -> None:
        self.next_token = self.get_token()
        while self.next_token[0] == "PROCEDURE":
            self.root.add_child(next(self.procedure()))
        self.statement_table.sort(key=lambda element: element['statement_line'])
        for child in self.proc_table:
            if not self.mod_table.get(child['proc_name'], None):
                self.mod_table[child['proc_name']] = {}
            if not self.uses_table.get(child['proc_name'], None):
                self.uses_table[child['proc_name']] = {}
            for proc in self.get_called_from_procedure(child['proc_name']):
                if self.mod_table.get(proc, None):
                    self.mod_table[child['proc_name']].update(self.mod_table[proc])
                if self.uses_table.get(proc, None):
                    self.uses_table[child['proc_name']].update(self.uses_table[proc])
            if self.mod_table.get(child['proc_name'], None) == {}:
                self.mod_table.pop(child['proc_name'], None)
            if self.uses_table.get(child['proc_name'], None) == {}:
                self.uses_table.pop(child['proc_name'], None)
        for statement in self.statement_table:
            if statement['other_info']['name'] == 'CALL':
                if self.mod_table.get(statement['other_info']['value'], None):
                    modified_vars: List[str] = self.mod_table[statement['other_info']['value']]
                    if not self.mod_table.get(str(statement['statement_line']), None):
                        self.mod_table[str(statement['statement_line'])] = modified_vars
                    else:
                        self.mod_table[str(statement['statement_line'])].update(modified_vars)
                if self.uses_table.get(statement['other_info']['value'], None):
                    used_vars: List[str] = self.uses_table[statement['other_info']['value']]
                    if not self.uses_table.get(str(statement['statement_line']), None):
                        self.uses_table[str(statement['statement_line'])] = used_vars
                    else:
                        self.uses_table[str(statement['statement_line'])].update(used_vars)
            elif statement['other_info']['name'] == 'WHILE' or statement['other_info']['name'] == 'IF':
                statements_inside_statement: List = [self.statement_table[i] for i in
                                                     range(statement['other_info']['start'],
                                                           statement['other_info']['end'])]
                for stmt in statements_inside_statement:
                    if stmt['other_info']['name'] == 'CALL':
                        if self.mod_table.get(stmt['other_info']['value'], None):
                            modified_vars: Dict = {x: y for x, y in self.mod_table[stmt['other_info']['value']].items()}
                            if not self.mod_table.get(str(statement['statement_line']), None):
                                self.mod_table[str(statement['statement_line'])] = modified_vars
                            else:
                                self.mod_table[str(statement['statement_line'])].update(modified_vars)
                        if self.uses_table.get(stmt['other_info']['value'], None):
                            used_vars: List[str] = {x: y for x, y in
                                                    self.uses_table[stmt['other_info']['value']].items()}
                            if not self.uses_table.get(str(statement['statement_line']), None):
                                self.uses_table[str(statement['statement_line'])] = used_vars
                            else:
                                self.uses_table[str(statement['statement_line'])].update(used_vars)

    def get_called_from_procedure(self, calls_procedure: str) -> List[str]:
        procedures_to_check: Set[str] = self.calls_table.get(calls_procedure, None)
        if procedures_to_check:
            procedures_to_check = procedures_to_check.keys()
            result: List[str] = list(procedures_to_check)
            for procedure in procedures_to_check:
                result.extend(self.get_called_from_procedure(procedure))
            return list(set(result))
        return []

    def procedure(self) -> Node:
        self.match("PROCEDURE")
        self.match("NAME")
        proc_node: Node = Node("PROCEDURE", self.prev_token[1])
        self.call_procedure = proc_node.value
        self.match("OPEN_BRACKET")
        start = self.current_line + 1
        proc_node.add_child(next(self.statement_list()))
        self.proc_table.append(
            {'proc_name': proc_node.value, 'other_info': {'start': start, 'finish': self.current_line}})
        self.match("CLOSE_BRACKET")
        yield proc_node

    def statement_list(self) -> Node:
        stmt_list_node: Node = Node("STMT_LIST", self.prev_token[1])
        prev_node: Node = None
        while self.next_token[0] != "CLOSE_BRACKET":
            stmt_node = next(self.statement())
            if prev_node is not None:
                if prev_node.node_type == 'IF':
                    for line in self.get_all_possible_endings(prev_node):
                        if not self.next_table.get(stmt_node.line, None):
                            self.next_table[stmt_node.line] = {line: 1}
                        else:
                            self.next_table[stmt_node.line][line] = 1
                else:
                    if not self.next_table.get(stmt_node.line, None):
                        self.next_table[stmt_node.line] = {prev_node.line: 1}
                    else:
                        self.next_table[stmt_node.line][prev_node.line] = 1
                self.follows_table[prev_node.line] = {stmt_node.line: 1}
            stmt_list_node.add_child(stmt_node)
            prev_node = stmt_node
        yield stmt_list_node

    def statement(self) -> Node:
        self.current_line += 1
        if self.next_token[0] == "WHILE":
            yield next(self.while_statement())
        elif self.next_token[0] == "CALL":
            yield next(self.call())
        elif self.next_token[0] == "IF":
            yield next(self.if_statement())
        else:
            yield next(self.assignment())

    def call(self) -> Node:
        self.match("CALL")
        if not self.calls_table.get(self.call_procedure, None):
            self.calls_table[self.call_procedure] = {self.next_token[1].strip(): 1}
        else:
            self.calls_table[self.call_procedure][self.next_token[1].strip()] = 1
        self.match("NAME")
        call_node: Node = Node("CALL", self.prev_token[1], self.current_line)
        self.statement_table.append({'statement_line': self.current_line, 'other_info':
            {'name': 'CALL', 'value': call_node.value, 'start': self.current_line,
             'end': self.current_line}})
        self.match("SEMICOLON")
        yield call_node

    def while_statement(self) -> Node:
        self.match("WHILE")
        self.match("NAME")
        while_node: Node = Node("WHILE", line=self.current_line)
        while_node.add_child(Node(self.prev_token[0], self.prev_token[1], self.current_line))

        self.var_table.add(self.prev_token[1])
        if not self.uses_table.get(str(self.current_line), None):
            self.uses_table[str(self.current_line)] = {self.prev_token[1]: 1}
        else:
            self.uses_table[str(self.current_line)][self.prev_token[1]] = 1
        if not self.uses_table.get(self.call_procedure, None):
            self.uses_table[self.call_procedure] = {self.prev_token[1]: 1}
        else:
            self.uses_table[self.call_procedure][self.prev_token[1]] = 1
        self.match("OPEN_BRACKET")
        if not self.next_table.get(self.current_line + 1, None):
            self.next_table[self.current_line + 1] = {while_node.line: 1}
        else:
            self.next_table[self.current_line + 1].update({while_node.line: 1})
        while_node.add_child(next(self.statement_list()))
        self.statement_table.append(
            {'statement_line': while_node.line, 'other_info': {'name': 'WHILE', 'value': while_node.children[0].value,
                                                               'start': while_node.line, 'end': self.current_line}})
        if while_node.children[1].children[-1].node_type == 'IF':
            for line in self.get_all_possible_endings(while_node.children[1].children[-1]):
                if not self.next_table.get(while_node.line, None):
                    self.next_table[while_node.line] = {line: 1}
                else:
                    self.next_table[while_node.line][line] = 1
        else:
            if not self.next_table.get(while_node.line, None):
                self.next_table[while_node.line] = {while_node.children[1].children[-1].line: 1}
            else:
                self.next_table[while_node.line][while_node.children[1].children[-1].line] = 1
        self.parent_table[while_node.line] = {}
        self.mod_table[str(while_node.line)] = {}
        for child in while_node.children[1].children:
            self.parent_table[while_node.line][child.line] = 1
            if child.node_type == 'ASSIGN' or child.node_type == 'WHILE' or child.node_type == 'IF':
                for letter in self.mod_table.get(str(child.line), []):
                    self.mod_table[str(while_node.line)][letter] = 1
                    self.mod_table[self.call_procedure][letter] = 1
                for letter in self.uses_table.get(str(child.line), []):
                    self.uses_table[str(while_node.line)][letter] = 1
                    self.uses_table[self.call_procedure][letter] = 1
        self.match("CLOSE_BRACKET")

        yield while_node

    def assignment(self) -> Node:
        assign_node: Node = Node("ASSIGN", line=self.current_line)
        self.match("NAME")
        assign_node.add_child(Node(self.prev_token[0], self.prev_token[1], self.current_line))
        self.var_table.add(self.prev_token[1])
        self.mod_table[str(self.current_line)] = {self.prev_token[1]: 1}
        if not self.mod_table.get(self.call_procedure, None):
            self.mod_table[self.call_procedure] = {self.prev_token[1]: 1}
        else:
            self.mod_table[self.call_procedure][self.prev_token[1]] = 1
        self.statement_table.append(
            {'statement_line': self.current_line, 'other_info': {'name': 'ASSIGN', 'value': self.prev_token[1],
                                                                 'start': self.current_line, 'end': self.current_line}})
        self.match("ASSIGN")
        assign_node.add_child(next(self.expression()))
        self.match("SEMICOLON")
        yield assign_node

    def get_all_possible_endings(self, node: Node) -> list:
        if node.node_type == 'IF':
            for x in self.get_all_possible_endings(node.children[1].children[-1]):
                yield x
            for x in self.get_all_possible_endings(node.children[2].children[-1]):
                yield x
        else:
            yield node.line

    def if_statement(self) -> Node:
        if_node: Node = Node("IF", line=self.current_line)
        self.match("IF")
        self.match("NAME")
        if_node.add_child(Node(self.prev_token[0], self.prev_token[1], self.current_line))
        if not self.uses_table.get(str(self.current_line), None):
            self.uses_table[str(self.current_line)] = {self.prev_token[1]: 1}
        else:
            self.uses_table[str(self.current_line)][self.prev_token[1]] = 1
        if not self.uses_table.get(self.call_procedure, None):
            self.uses_table[self.call_procedure] = {self.prev_token[1]: 1}
        else:
            self.uses_table[self.call_procedure][self.prev_token[1]] = 1
        self.var_table.add(self.prev_token[1])
        self.match("THEN")
        self.match("OPEN_BRACKET")
        if not self.next_table.get(self.current_line + 1, None):
            self.next_table[self.current_line + 1] = {if_node.line: 1}
        else:
            self.next_table[self.current_line + 1].update({if_node.line: 1})
        if_node.add_child(next(self.statement_list()))
        last_if_line: int = self.find_last_child_line_number(if_node.children[1])
        self.parent_table[if_node.line] = {}
        self.mod_table[str(if_node.line)] = {}
        for child in if_node.children[1].children:
            self.parent_table[if_node.line][child.line] = 1
            if child.node_type == 'ASSIGN' or child.node_type == 'WHILE' or child.node_type == 'IF':
                for letter in self.mod_table.get(str(child.line), []):
                    self.mod_table[str(if_node.line)][letter] = 1
                    self.mod_table[self.call_procedure][letter] = 1
                for letter in self.uses_table.get(str(child.line), []):
                    self.uses_table[str(if_node.line)][letter] = 1
                    self.uses_table[self.call_procedure][letter] = 1
        self.match("CLOSE_BRACKET")
        self.match("ELSE")
        self.match("OPEN_BRACKET")
        if not self.next_table.get(self.current_line + 1, None):
            self.next_table[self.current_line + 1] = {if_node.line: 1}
        else:
            self.next_table[self.current_line + 1].update({if_node.line: 1})
        if_node.add_child(next(self.statement_list()))
        last_else_line: int = self.find_last_child_line_number(if_node.children[2])
        for child in if_node.children[2].children:
            self.parent_table[if_node.line][child.line] = 1
            if child.node_type == 'ASSIGN' or child.node_type == 'WHILE' or child.node_type == 'IF':
                for letter in self.mod_table.get(str(child.line), []):
                    self.mod_table[str(if_node.line)][letter] = 1
                    self.mod_table[self.call_procedure][letter] = 1
                for letter in self.uses_table.get(str(child.line), []):
                    self.uses_table[str(if_node.line)][letter] = 1
                    self.uses_table[self.call_procedure][letter] = 1
        self.match("CLOSE_BRACKET")
        self.statement_table.append({'statement_line': if_node.line,
                                     'other_info': {'name': 'IF', 'value': if_node.children[0].value,
                                                    'start': if_node.line, 'end': self.current_line,
                                                    'last_else_line': last_else_line,
                                                    'last_if_line': last_if_line}})
        yield if_node

    def find_last_child_line_number(self, node: Node):
        last_line: int = node.line
        if not node.children:
            return last_line
        else:
            children_lines = [self.find_last_child_line_number(child) for child in node.children]
            value = max(children_lines)
            return value

    def expression(self) -> Node:
        node: Node = next(self.term())
        while self.next_token[0] in ["PLUS", "MINUS"]:
            op_node: Node = Node(self.next_token[0], self.next_token[1].strip(), line=self.current_line)
            self.match(self.next_token[0])
            op_node.add_child(node)
            op_node.add_child(next(self.term()))
            node = op_node
        yield node

    def term(self) -> Node:
        node: Node = next(self.factor())
        while self.next_token[0] == "MULTIPLY":
            multiply_node: Node = Node(self.next_token[0], self.next_token[1], self.current_line)
            self.match("MULTIPLY")
            multiply_node.add_child(node)
            multiply_node.add_child(next(self.factor()))
            node = multiply_node
        yield node

    def factor(self) -> Node:
        try:
            if self.next_token[0] == "OPEN_PARENTHESIS":
                self.match("OPEN_PARENTHESIS")
                factor_node: Node = next(self.expression())
                self.match("CLOSE_PARENTHESIS")
                yield factor_node
            elif self.next_token[0] == "INTEGER":
                self.match("INTEGER")
                if self.const_table.get(self.prev_token[1], None):
                    self.const_table[self.prev_token[1]]['lines'].append(self.current_line)
                else:
                    self.const_table[self.prev_token[1]] = {'lines': [self.current_line]}

                yield Node(self.prev_token[0], self.prev_token[1], self.current_line)
            elif self.next_token[0] == "NAME":
                self.match("NAME")
                if not self.uses_table.get(str(self.current_line), None):
                    self.uses_table[str(self.current_line)] = {self.prev_token[1]: 1}
                else:
                    self.uses_table[str(self.current_line)][self.prev_token[1]] = 1
                if not self.uses_table.get(self.call_procedure, None):
                    self.uses_table[self.call_procedure] = {self.prev_token[1]: 1}
                else:
                    self.uses_table[self.call_procedure][self.prev_token[1]] = 1
                self.var_table.add(self.prev_token[1])
                yield Node(self.prev_token[0], self.prev_token[1], self.current_line)
            else:
                raise Exception(
                    f"Line {self.current_line}: Expected a variable or integer but received '{self.next_token[2]}'.")
        except Exception:
            log.exception("SyntaxError")
            raise Exception("Check logs for more info")

    def get_node_json(self) -> Dict[str, dict]:
        json_str = Node.Schema().dumps(self.root)
        json_dict: Dict[str, dict] = json.loads(json_str)
        return json_dict
