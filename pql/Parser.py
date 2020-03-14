from pql.Node import Node


class Parser:
    # znacznik * jest przekształcony na litere T(np. Follows* == FOLLOWST)
    token_expressions = [(r'\s*Select', 'SELECT'), (r'\s*such that', 'SUCH_THAT'),
                         (r"\s*Follows", 'FOLLOWS'), (r'\s*Parent', 'PARENT'), (r'\s*Modifies', 'MODIFIES'),
                         (r'\s*Uses', 'USES'), (r'\s*CallS', 'CALLS'),
                         (r'\s*Follows*', 'FOLLOWST'), (r'\s*Parent*', 'PARENTT'), (r'\s*Modifies*', 'MODIFIEST'),
                         (r'\s*Uses*', 'USEST'), (r'\s*CallS*', 'CALLST'),
                         (r'\s*\(', 'OPEN_PARENTHESIS'), (r'\s*\)', 'CLOSE_PARENTHESIS'), (r'\s*;', 'SEMICOLON'),
                         (r"\s*=", "EQUALS_SIGN"),
                         (r'\s*[A-Za-z]+[A-Za-z0-9]*', 'NAME'), (r'\s*[A-Za-z]+[A-Za-z0-9#]*', 'IDENT'),
                         (r'\s*_', 'EVERYTHING'), (r'\s*"', 'QUOTE'),
                         (r'\s*if', 'IF'), (r'\s*while', 'WHILE'), (r'\s*assign', 'ASSIGN'),
                         (r'\s*procedure', 'PROCEDURE'), (r'\s*call', 'CALL'), (r'\s*stmt', 'STMT'),
                         (r'\s*variable', 'VARIABLE'), (r'\s*BOOLEAN', 'BOOLEAN'), (r'\s*constant', 'CONSTANT'),
                         (r'\s*prog_line', 'PROG_LINE'),
                         (r'\s*with', 'WITH'), (r'\s*and', 'AND'), (r'\s*[0-9]+', 'INTEGER')]

    def __init__(self) -> None:
        # todo inicjalizacja
        pass

    def parse(self, query: str) -> str:
        pass

    def stmt_ref(self) -> Node:
        pass

    def ent_ref(self) -> Node:
        pass

    def select_cl(self) -> Node:
        pass

    def declaration(self) -> Node:
        pass

    def such_that_cl(self) -> Node:
        pass

    def rel_ref(self) -> Node:
        pass

    def modifies(self) -> Node:
        pass

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
