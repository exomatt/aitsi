import json
import logging
import re
from typing import Tuple, Dict, List

from pql.Node import Node

log = logging.getLogger(__name__)


class QueryProcessor:
    # znacznik * jest przekształcony na litere T(np. Follows* == FOLLOWST)
    token_expressions = [(r'\s*Select', 'SELECT'), (r'\s*such that', 'SUCH_THAT'),
                         (r'\s*pattern', 'PATTERN'), (r"\s*\+", "PLUS"), (r"\s*\-", "MINUS"),
                         (r"\s*\*", "MULTIPLY"),
                         (r'\s*Follows\*', 'FOLLOWST'), (r'\s*Parent\*', 'PARENTT'), (r'\s*Modifies\*', 'MODIFIEST'),
                         (r'\s*Uses\*', 'USEST'), (r'\s*Calls\*', 'CALLST'), (r'\s*Next\*', 'NEXTT'),
                         (r"\s*Follows", 'FOLLOWS'), (r'\s*Parent', 'PARENT'), (r'\s*Modifies', 'MODIFIES'),
                         (r'\s*Uses', 'USES'), (r'\s*Calls', 'CALLS'), (r'\s*Next', 'NEXT'),
                         (r'\s*\(', 'OPEN_PARENTHESIS'), (r'\s*\)', 'CLOSE_PARENTHESIS'), (r'\s*;', 'SEMICOLON'),
                         (r"\s*=", "EQUALS_SIGN"),
                         (r'\s*_', 'EVERYTHING'),
                         (r'.stmt#|.value|.procName|.varName', 'ATTR_NAME'),
                         (
                             r'\s*while\s|\s*assign\s|\s*stmt\s|\s*variable\s|\s*constant\s|\s*procedure\s|\s*prog_line\s|\s*call\s|\s*if\s',
                             'DECLARATION'),
                         (r'\s*BOOLEAN', 'BOOLEAN'),
                         (r'\s*with', 'WITH'), (r'\s*and', 'AND'),
                         (r'\s*"[A-Za-z]+[A-Za-z0-9#]*"', 'IDENT_QUOTE'), (r'\s*\"', "QUOTE"),
                         (r'\s*[A-Za-z]+[A-Za-z0-9\#]*', 'IDENT'),
                         (r'\s*[0-9]+', 'INTEGER'), (r'\s*,', 'COMMA'), (r'\s*\.', 'DOT')]

    def __init__(self, proc_names: List[str], var_names: List[str], max_line_in_code: int) -> None:
        self.pos: int = 0
        self.query: str = None
        self.prev_token: Tuple[str, str] = ('', '')
        self.next_token: Tuple[str, str] = ('', '')
        self.root: Node = Node("QUERY", "query")
        self.declaration_dict: Dict[str, str] = {}
        self.proc_names: List[str] = proc_names
        self.var_names: List[str] = var_names
        self.max_line_in_code: int = max_line_in_code

    def match(self, token: str) -> None:
        if self.next_token[0] == token:
            self.prev_token = self.next_token
            self.next_token = self.get_token()
        else:
            self.error(self.next_token[0] + "not equals " + token)

    def error(self, info: str) -> None:
        log.error("ERROR: " + info)

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

    def generate_query_tree(self, query: str) -> None:
        self.query = query.replace('\n', '')
        self.next_token = self.get_token()
        self.select_cl()
        self.root.to_log(0)

    def stmt_ref(self) -> Node:
        if self.next_token[0] == "IDENT":
            self.synonym()
            declaration_variable_type: str = self.get_declaration_type(self.prev_token[1].strip())
            if declaration_variable_type is None:
                self.error("stmt_ref ")
            if declaration_variable_type not in ["STMT", "CONSTANT", "WHILE", "IF", "PROG_LINE", "ASSIGN",
                                                 "CALL"]:
                self.error("stmt_ref error - bad agrument - argument must be integer")
            return Node(declaration_variable_type, self.prev_token[1].strip())
        elif self.next_token[0] == "EVERYTHING":
            self.match("EVERYTHING")
        elif self.next_token[0] == "INTEGER":
            if not self.if_line_is_in_code(int(self.next_token[1].strip())):
                self.error("line " + self.next_token[1].strip() + " is out of bound")
            self.match("INTEGER")
        return Node(self.prev_token[0].strip(), self.prev_token[1].strip())

    def ent_ref(self) -> Node:
        if self.next_token[0] == "IDENT":
            self.synonym()
            declaration_variable_type: str = self.get_declaration_type(self.prev_token[1].strip())
            if declaration_variable_type is None:
                self.error("ent_ref ")
            return Node(declaration_variable_type, self.prev_token[1].strip())
        elif self.next_token[0] == "EVERYTHING":
            self.match("EVERYTHING")
        elif self.next_token[0] == "IDENT_QUOTE":
            self.match("IDENT_QUOTE")
        elif self.next_token[0] == "INTEGER":
            if not self.if_line_is_in_code(int(self.next_token[1].strip())):
                self.error("line" + self.next_token[1].strip() + "is out of bound")
            self.match("INTEGER")

        return Node(self.prev_token[0].strip(), self.prev_token[1].strip().replace('"', ''))

    def line_ref(self) -> Node:
        if self.next_token[0] == "IDENT":
            self.synonym()
            declaration_variable_type: str = self.get_declaration_type(self.prev_token[1].strip())
            if declaration_variable_type is None:
                self.error("stmt_ref ")
            if declaration_variable_type not in ["STMT", "CONSTANT", "WHILE", "IF", "PROG_LINE", "ASSIGN",
                                                 "CALL"]:
                self.error("stmt_ref error - bad agrument - argument must be integer")
            return Node(declaration_variable_type, self.prev_token[1].strip())
        elif self.next_token[0] == "EVERYTHING":
            self.match("EVERYTHING")
        elif self.next_token[0] == "INTEGER":
            if not self.if_line_is_in_code(int(self.next_token[1].strip())):
                self.error("line " + self.next_token[1].strip() + " is out of bound")
            self.match("INTEGER")
        return Node(self.prev_token[0].strip(), self.prev_token[1].strip())

    def proc_ref(self) -> Node:
        if self.next_token[0] == "IDENT":
            self.synonym()
            declaration_variable_type: str = self.get_declaration_type(self.prev_token[1].strip())
            if declaration_variable_type is None:
                self.error("ent_ref ")
            if declaration_variable_type not in ["PROCEDURE"]:
                self.error("proc ref error - argument must be procedure ")
            return Node(declaration_variable_type, self.prev_token[1].strip())
        elif self.next_token[0] == "EVERYTHING":
            self.match("EVERYTHING")
        elif self.next_token[0] == "IDENT_QUOTE":
            if self.next_token[1].strip().replace('"', '') not in self.proc_names:
                self.error(self.next_token[1].strip().replace('"', '') + " procedure not exist")
            self.match("IDENT_QUOTE")

        return Node(self.prev_token[0].strip(), self.prev_token[1].strip().replace('"', ''))

    def var_ref(self) -> Node:
        if self.next_token[0] == "IDENT":
            self.synonym()
            declaration_variable_type: str = self.get_declaration_type(self.prev_token[1].strip())
            if declaration_variable_type is None:
                self.error("ent_ref ")
            if declaration_variable_type not in ["VARIABLE"]:
                self.error("var ref error - argument must be variable ")
            return Node(declaration_variable_type, self.prev_token[1].strip())
        elif self.next_token[0] == "EVERYTHING":
            self.match("EVERYTHING")
        elif self.next_token[0] == "IDENT_QUOTE":
            if self.next_token[1].strip().replace('"', '') not in self.var_names:
                self.error(self.next_token[1].strip().replace('"', '') + " variable not exist")
            self.match("IDENT_QUOTE")

        return Node(self.prev_token[0].strip(), self.prev_token[1].strip().replace('"', ''))

    def select_cl(self) -> None:
        self.design_entity()
        self.match("SELECT")
        result_node: Node = Node("RESULT")
        if self.next_token[0] == 'BOOLEAN':
            self.match('BOOLEAN')
            result_node.add_child(Node('BOOLEAN', 'BOOLEAN'))
        else:
            self.synonym()
            declaration_variable_type: str = self.get_declaration_type(self.prev_token[1].strip())
            if declaration_variable_type is None:
                self.error("select_cl ")
            result_node.add_child(Node(declaration_variable_type, self.prev_token[1].strip()))
        self.root.add_child(result_node)
        such_that_node: Node = Node("SUCH_THAT")
        with_node: Node = Node("WITH")
        pattern_node: Node = Node("PATTERN")
        while self.next_token[0] in ["SUCH_THAT", "WITH", "PATTERN"]:
            if self.next_token[0] == "SUCH_THAT":
                self.match("SUCH_THAT")
                such_that_node.add_children(self.such_that_cl())
            if self.next_token[0] == "WITH":
                self.match("WITH")
                with_node.add_children(self.with_cl())
            if self.next_token[0] == "PATTERN":
                self.match("PATTERN")
                pattern_node.add_children(self.pattern_cl())
        if with_node.children:
            self.root.add_child(with_node)
        if pattern_node.children:
            self.root.add_child(pattern_node)
        if such_that_node.children:
            self.root.add_child(such_that_node)

    def get_declaration_type(self, variable_name: str) -> str:
        return self.declaration_dict.get(variable_name, "")

    def declaration(self) -> None:
        variable_type: str = self.prev_token[1].upper().strip()
        while self.next_token[0] != "SEMICOLON":
            if self.next_token[1].strip() in self.declaration_dict:
                self.error("Variable " + self.next_token[1].strip() + " already exist")
            else:
                self.declaration_dict.update({self.next_token[1].strip(): variable_type})
            self.synonym()
            if self.next_token[0] == "COMMA":
                self.match("COMMA")
        self.match("SEMICOLON")

    def design_entity(self) -> None:
        while self.next_token[0] != "SELECT":
            if self.next_token[0] == "DECLARATION":
                self.match("DECLARATION")
                self.declaration()

    def such_that_cl(self) -> List[Node]:
        node_list: List[Node] = [self.rel_ref()]
        while self.next_token[0] == "AND":
            self.match("AND")
            node_list.append(self.rel_ref())
        return node_list

    def pattern_cl(self) -> List[Node]:
        node_list: List[Node] = [self.pattern_cond()]
        while self.next_token[0] == "AND":
            self.match("AND")
            node_list.append(self.pattern_cond())
        return node_list

    def pattern_cond(self) -> Node:
        if self.next_token[0] == "IDENT":
            self.synonym()
            declaration_variable_type: str = self.get_declaration_type(self.prev_token[1].strip())
            if declaration_variable_type is None:
                self.error("pattern_cond error - variable " + self.prev_token[1].strip() + " not declared")
            if declaration_variable_type == "ASSIGN":
                return self.assign_cond()
            elif declaration_variable_type == "IF":
                return self.if_cond()
            elif declaration_variable_type == "WHILE":
                return self.while_cond()
            else:
                self.error("Pattern syntax error - " + self.prev_token[1].strip() + " must be ASSIG IF or WHILE")
        else:
            self.error("pattern_cond error - token must be a synonym")

    def assign_cond(self) -> Node:
        pattern_assign_node = Node("PATTERN_ASSIGN")
        pattern_assign_node.add_child(Node('ASSIGN', self.prev_token[1].strip()))
        argument1_node: Node
        argument2_node: Node
        self.match("OPEN_PARENTHESIS")
        argument1_node = self.var_ref()
        self.match("COMMA")
        if self.next_token[0] == "EVERYTHING":
            self.match("EVERYTHING")
            argument2_node = Node(self.prev_token[0].strip(), self.prev_token[1].strip())
            if self.next_token[0] is "IDENT_QUOTE":
                argument2_node.add_child(self.expression())
                self.match("EVERYTHING")
            elif self.next_token[0] is "QUOTE":
                self.match("QUOTE")
                argument2_node.add_child(self.expression())
                self.match("QUOTE")
                self.match("EVERYTHING")
        else:
            if self.next_token[0] is "IDENT_QUOTE":
                argument2_node = self.expression()
            else:
                self.match("QUOTE")
                argument2_node = self.expression()
                self.match("QUOTE")
        self.match("CLOSE_PARENTHESIS")
        pattern_assign_node.add_child(argument1_node)
        pattern_assign_node.add_child(argument2_node)
        return pattern_assign_node

    def expression(self) -> Node:
        node: Node = self.term()
        while self.next_token[0] in ["PLUS", "MINUS"]:
            op_node: Node = Node(self.next_token[0], self.next_token[1].strip())
            self.match(self.next_token[0])
            op_node.add_child(node)
            op_node.add_child(self.term())
            node = op_node
        return node

    def term(self) -> Node:
        node: Node = self.factor()
        while self.next_token[0] == "MULTIPLY":
            multiply_node: Node = Node(self.next_token[0], self.next_token[1])
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
            return Node(self.prev_token[0], self.prev_token[1])
        elif self.next_token[0] == "IDENT":
            self.match("IDENT")
            return Node("NAME", self.prev_token[1])
        elif self.next_token[0] == "IDENT_QUOTE":
            self.match("IDENT_QUOTE")
            return Node("NAME", self.prev_token[1].replace('"', '').strip())

    def if_cond(self) -> Node:
        pattern_if_node = Node("PATTERN_IF")
        pattern_if_node.add_child(Node('IF', self.prev_token[1].strip()))
        argument1_node: Node
        argument2_node: Node
        argument3_node: Node
        self.match("OPEN_PARENTHESIS")
        argument1_node = self.var_ref()
        self.match("COMMA")
        if self.next_token[0] == "EVERYTHING":
            self.match("EVERYTHING")
            argument2_node = Node(self.prev_token[0].strip(), self.prev_token[1].strip())
            self.match("COMMA")
        else:
            self.error("Second argument must be _")
        if self.next_token[0] == "EVERYTHING":
            self.match("EVERYTHING")
            argument3_node = Node(self.prev_token[0].strip(), self.prev_token[1].strip())
        else:
            self.error("Third argument must be _")
        self.match("CLOSE_PARENTHESIS")
        pattern_if_node.add_child(argument1_node)
        pattern_if_node.add_child(argument2_node)
        pattern_if_node.add_child(argument3_node)
        return pattern_if_node

    def while_cond(self) -> Node:
        pattern_while_node = Node("PATTERN_WHILE")
        pattern_while_node.add_child(Node('WHILE', self.prev_token[1].strip()))
        argument1_node: Node
        argument2_node: Node
        self.match("OPEN_PARENTHESIS")
        argument1_node = self.var_ref()
        self.match("COMMA")
        if self.next_token[0] == "EVERYTHING":
            self.match("EVERYTHING")
            argument2_node = Node(self.prev_token[0].strip(), self.prev_token[1].strip().replace('"', ''))
        else:
            self.error("Second argument must be _")
        self.match("CLOSE_PARENTHESIS")
        pattern_while_node.add_child(argument1_node)
        pattern_while_node.add_child(argument2_node)
        return pattern_while_node

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
        elif self.next_token[0] == "CALLS":
            return self.relation_with_the_same_arguments("CALLS")
        elif self.next_token[0] == "CALLST":
            return self.relation_with_the_same_arguments("CALLST")
        elif self.next_token[0] == "NEXT":
            return self.relation_with_the_same_arguments("NEXT")
        elif self.next_token[0] == "NEXTT":
            return self.relation_with_the_same_arguments("NEXTT")

    def relation_with_the_same_arguments(self, type_node: str) -> Node:
        self.match(type_node)
        relation_node: Node = Node(type_node)
        self.match("OPEN_PARENTHESIS")
        # relation_node.add_child(self.stmt_ref())
        # self.match("COMMA")
        # relation_node.add_child(self.stmt_ref())
        argument1_node: Node
        argument2_node: Node
        if type_node in ["PARENT", "PARENTT", "FOLLOWS", "FOLLOWST"]:
            argument1_node = self.stmt_ref()
            relation_node.add_child(argument1_node)
            self.match("COMMA")
            argument2_node: Node = self.stmt_ref()
            relation_node.add_child(argument2_node)
        elif type_node in ["CALLS", "CALLST"]:
            argument1_node = self.proc_ref()
            relation_node.add_child(argument1_node)
            self.match("COMMA")
            argument2_node: Node = self.proc_ref()
            relation_node.add_child(argument2_node)
        elif type_node in ["NEXT", "NEXTT"]:
            argument1_node = self.line_ref()
            relation_node.add_child(argument1_node)
            self.match("COMMA")
            argument2_node: Node = self.line_ref()
            relation_node.add_child(argument2_node)
        self.match("CLOSE_PARENTHESIS")
        if argument1_node.node_type == "EVERYTHING" and argument2_node.node_type == "EVERYTHING":
            self.error("Error - relation with both arguments '_' is invalid")
        return relation_node

    def relation_with_other_arguments(self, type_node: str) -> Node:
        self.match(type_node)
        relation_node: Node = Node(type_node)
        self.match("OPEN_PARENTHESIS")
        # relation_node.add_child(self.stmt_ref())
        # self.match("COMMA")
        # relation_node.add_child(self.ent_ref())
        argument1_node: Node
        argument2_node: Node
        if type_node in ["MODIFIES", "MODIFIEST", "USES", "USEST"]:
            if self.next_token[0] == "IDENT":
                declaration_variable_type: str = self.get_declaration_type(self.next_token[1].strip())
                if declaration_variable_type == "PROCEDURE":
                    argument1_node = self.proc_ref()
                else:
                    argument1_node = self.stmt_ref()
            elif self.next_token[0] == "INTEGER":
                argument1_node = self.stmt_ref()
            else:
                argument1_node = self.proc_ref()
            relation_node.add_child(argument1_node)
            self.match("COMMA")
            argument2_node: Node = self.var_ref()
            relation_node.add_child(argument2_node)
        self.match("CLOSE_PARENTHESIS")
        if argument1_node.node_type == "EVERYTHING":
            self.error("Error - in this relation _ as first argument is invalid")
        return relation_node

    def with_cl(self) -> List[Node]:
        node_list: List[Node] = [self.attribute()]
        while self.next_token[0] == "AND":
            self.match("AND")
            node_list.append(self.attribute())
        return node_list

    def attribute(self) -> Node:
        attribute_node: Node = Node("ATTR")
        self.synonym()
        declaration_variable_type: str = self.get_declaration_type(self.prev_token[1].strip())
        if declaration_variable_type is None:
            self.error("attribute ")
        synonym_node: Node = Node(declaration_variable_type, self.prev_token[1].strip())
        if self.validate_attribute_name(declaration_variable_type) is False:
            self.error("attribute validate error")
        else:
            synonym_node.add_child(self.attr_name())
        attribute_node.add_child(synonym_node)
        attribute_node.add_child(self.ref())
        if attribute_node.children[1].node_type == "IDENT_QUOTE":
            if synonym_node.node_type in ["PROCEDURE", "CALL"]:
                if attribute_node.children[1].value not in self.proc_names:
                    self.error(attribute_node.children[1].value + " procedure not exist")
            elif synonym_node.node_type == "VARIABLE":
                if attribute_node.children[1].value not in self.var_names:
                    self.error(attribute_node.children[1].value + " variable not exist")
        elif attribute_node.children[1].node_type == "INTEGER":
            if not self.if_line_is_in_code(int(attribute_node.children[1].value)):
                self.error("line " + attribute_node.children[1].value + " is out of bound")
        return attribute_node

    def attr_name(self) -> Node:
        self.match('ATTR_NAME')
        return Node(self.prev_token[0], self.prev_token[1].replace('.', ''))

    def attribute_value(self) -> Node:
        self.synonym()
        declaration_variable_type: str = self.get_declaration_type(self.prev_token[1].strip())
        if declaration_variable_type is None:
            self.error("attribute_value ")
        synonym_node: Node = Node(declaration_variable_type, self.prev_token[1].strip())
        if not self.validate_attribute_name(declaration_variable_type):
            self.error("attribute_value validate error")
        else:
            synonym_node.add_child(self.attr_name_value())
        return synonym_node

    def attr_name_value(self) -> Node:
        self.match('ATTR_NAME')
        attr_name_node: Node = Node(self.prev_token[0], self.prev_token[1].replace('.', '').strip())
        return attr_name_node

    def ref(self) -> Node:
        self.match("EQUALS_SIGN")
        ref_node: Node = Node(self.next_token[0], self.next_token[1].replace('.', '').replace('"', ''))
        # if ref_node.value not in
        if self.next_token[0] == "IDENT_QUOTE":
            self.match("IDENT_QUOTE")
        elif self.next_token[0] == "INTEGER":
            self.match("INTEGER")
        elif self.next_token[0] == "IDENT":
            return self.attribute_value()
        return ref_node

    def synonym(self) -> None:
        self.match("IDENT")

    def validate_attribute_name(self, variable_type: str) -> bool:
        if variable_type in ["STMT", "WHILE", "IF", "ASSIGN", "CALL"] and self.next_token[1].replace('.',
                                                                                                     '').strip() == "stmt#":
            return True
        if variable_type == "CONSTANT" and self.next_token[1].replace('.', '').strip() == "value":
            return True
        if variable_type == "PROCEDURE" and self.next_token[1].replace('.', '').strip() == "procName":
            return True
        if variable_type == "VARIABLE" and self.next_token[1].replace('.', '').strip() == "varName":
            return True
        if variable_type == "CALL" and self.next_token[1].replace('.', '').strip() == "procName":
            return True
        return False

    def get_node_json(self) -> Dict[str, dict]:
        json_str = Node.Schema().dumps(self.root)
        json_dict: Dict[str, dict] = json.loads(json_str)
        return json_dict

    def if_line_is_in_code(self, line_number: int) -> bool:
        if line_number > self.max_line_in_code:
            return False
        return True
