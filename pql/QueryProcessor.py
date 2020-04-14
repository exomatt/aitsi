import json
import re
from typing import Tuple, Dict, List

from pql.Node import Node


class QueryProcessor:
    # znacznik * jest przekształcony na litere T(np. Follows* == FOLLOWST)
    token_expressions = [(r'\s*Select', 'SELECT'), (r'\s*such that', 'SUCH_THAT'),
                         (r'\s*Follows\*', 'FOLLOWST'), (r'\s*Parent\*', 'PARENTT'), (r'\s*Modifies\*', 'MODIFIEST'),
                         (r'\s*Uses\*', 'USEST'), (r'\s*Calls\*', 'CALLST'),
                         (r"\s*Follows", 'FOLLOWS'), (r'\s*Parent', 'PARENT'), (r'\s*Modifies', 'MODIFIES'),
                         (r'\s*Uses', 'USES'), (r'\s*Calls', 'CALLS'),
                         (r'\s*\(', 'OPEN_PARENTHESIS'), (r'\s*\)', 'CLOSE_PARENTHESIS'), (r'\s*;', 'SEMICOLON'),
                         (r"\s*=", "EQUALS_SIGN"),
                         (r'\s*_', 'EVERYTHING'),
                         (r'.stmt#|.value|.procName|.varName', 'ATTR_NAME'),
                         (r'\s*while|\s*assign|\s*stmt|\s*variable|\s*constant|\s*procedure|\s*prog_line|\s*call|\s*if',
                          'DECLARATION'),
                         (r'\s*BOOLEAN', 'BOOLEAN'),
                         (r'\s*with', 'WITH'), (r'\s*and', 'AND'),
                         (r'\s*"[A-Za-z]+[A-Za-z0-9#]*"', 'IDENT_QUOTE'), (r'\s*[A-Za-z]+[A-Za-z0-9\#]*', 'IDENT'),
                         (r'\s*[0-9]+', 'INTEGER'), (r'\s*,', 'COMMA'), (r'\s*\.', 'DOT')]

    def __init__(self) -> None:
        self.pos: int = 0
        self.query: str = None
        self.prev_token: Tuple[str, str] = ('', '')
        self.next_token: Tuple[str, str] = ('', '')
        self.root: Node = Node("QUERY", "query")
        self.declaration_dict: Dict[str, str] = {}

    def match(self, token: str) -> None:
        if self.next_token[0] == token:
            self.prev_token = self.next_token
            self.next_token = self.get_token()
        else:
            self.error(self.next_token[0] + "not equals " + token)

    def error(self, info: str) -> None:
        print("ERROR: " + info)

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
        # self.root.to_string(0) #todo można odkomentować żeby wypisac sobie dane cyk najlepiej zmienic na logi

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
            self.match("INTEGER")
        return Node(self.prev_token[0].strip(), self.prev_token[1].strip())

    def ent_ref(self) -> Node:
        if self.next_token[0] == "IDENT":
            self.synonym()
            declaration_variable_type: str = self.get_declaration_type(self.prev_token[1].strip())
            if declaration_variable_type is None:
                self.error("ent_ref ")
            if declaration_variable_type not in ["PROCEDURE", "VARIABLE"]:
                self.error("ent ref error - argument must be string ")
            return Node(declaration_variable_type, self.prev_token[1].strip())
        elif self.next_token[0] == "EVERYTHING":
            self.match("EVERYTHING")
        elif self.next_token[0] == "IDENT_QUOTE":
            self.match("IDENT_QUOTE")

        return Node(self.prev_token[0].strip(), self.prev_token[1].strip().replace('"', ''))

    def select_cl(self) -> None:
        self.design_entity()
        self.match("SELECT")
        result_node: Node = Node("RESULT")
        if self.next_token[0] == 'BOOLEAN':
            self.match('BOOLEAN')
        else:
            self.synonym()
            declaration_variable_type: str = self.get_declaration_type(self.prev_token[1].strip())
            if declaration_variable_type is None:
                self.error("select_cl ")
        result_node.add_child(Node(declaration_variable_type, self.prev_token[1].strip()))
        self.root.add_child(result_node)
        such_that_node: Node = Node("SUCH_THAT")
        with_node: Node = Node("WITH")
        while self.next_token[0] in ["SUCH_THAT", "WITH"]:
            if self.next_token[0] == "SUCH_THAT":
                self.match("SUCH_THAT")
                such_that_node.add_children(self.such_that_cl())
            if self.next_token[0] == "WITH":
                self.match("WITH")
                with_node.add_children(self.with_cl())
        if such_that_node.children:
            self.root.add_child(such_that_node)
        if with_node.children:
            self.root.add_child(with_node)

    def get_declaration_type(self, variable_name: str) -> str:
        return self.declaration_dict.get(variable_name, None)

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
            return self.relation_with_the_same_arguments_and_is_integer("PARENT")
        elif self.next_token[0] == "PARENTT":
            return self.relation_with_the_same_arguments_and_is_integer("PARENTT")
        elif self.next_token[0] == "FOLLOWS":
            return self.relation_with_the_same_arguments_and_is_integer("FOLLOWS")
        elif self.next_token[0] == "FOLLOWST":
            return self.relation_with_the_same_arguments_and_is_integer("FOLLOWST")
        elif self.next_token[0] == "CALLS":
            return self.relation_with_the_same_arguments_and_is_string("CALLS")
        elif self.next_token[0] == "CALLST":
            return self.relation_with_the_same_arguments_and_is_string("CALLST")

    def relation_with_the_same_arguments_and_is_integer(self, type_node: str) -> Node:
        self.match(type_node)
        relation_node: Node = Node(type_node)
        self.match("OPEN_PARENTHESIS")
        relation_node.add_child(self.stmt_ref())
        self.match("COMMA")
        relation_node.add_child(self.stmt_ref())
        self.match("CLOSE_PARENTHESIS")
        return relation_node

    def relation_with_the_same_arguments_and_is_string(self, type_node: str) -> Node:
        self.match(type_node)
        relation_node: Node = Node(type_node)
        self.match("OPEN_PARENTHESIS")
        relation_node.add_child(self.ent_ref())
        self.match("COMMA")
        relation_node.add_child(self.ent_ref())
        self.match("CLOSE_PARENTHESIS")
        return relation_node

    def relation_with_other_arguments(self, type_node: str) -> Node:
        self.match(type_node)
        relation_node: Node = Node(type_node)
        self.match("OPEN_PARENTHESIS")
        relation_node.add_child(self.stmt_ref())
        self.match("COMMA")
        relation_node.add_child(self.ent_ref())
        self.match("CLOSE_PARENTHESIS")
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
        ref_node: Node = Node(self.next_token[0], self.next_token[1].replace('.', ''))
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
