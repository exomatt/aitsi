from typing import List, Union, Dict, Tuple, Set

from aitsi_parser.CallsTable import CallsTable
from aitsi_parser.ConstTable import ConstTable
from aitsi_parser.FollowsTable import FollowsTable
from aitsi_parser.ModifiesTable import ModifiesTable
from aitsi_parser.NextTable import NextTable
from aitsi_parser.ParentTable import ParentTable
from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.UsesTable import UsesTable
from aitsi_parser.VarTable import VarTable
from pql.Node import Node
from pql.relations.CallsRelation import CallsRelation
from pql.relations.FollowsRelation import FollowsRelation
from pql.relations.ModifiesRelation import ModifiesRelation
from pql.relations.NextRelation import NextRelation
from pql.relations.ParentRelation import ParentRelation
from pql.relations.UsesRelation import UsesRelation
from pql.utils.SearchUtils import SearchUtils


class QueryEvaluator:

    def __init__(self, all_tables: Dict[str,
                                        Union[VarTable,
                                              ProcTable,
                                              UsesTable,
                                              ParentTable,
                                              ModifiesTable,
                                              FollowsTable,
                                              CallsTable,
                                              StatementTable,
                                              ConstTable,
                                              NextTable]],
                 ast_node: Node) -> None:
        self.ast_node = ast_node
        self.all_tables: Dict[str, Union[VarTable,
                                         ProcTable,
                                         UsesTable,
                                         ParentTable,
                                         ModifiesTable,
                                         FollowsTable,
                                         CallsTable,
                                         StatementTable,
                                         ConstTable,
                                         NextTable]] = all_tables
        self.results: Dict[str, Union[bool, Set[str], Set[int]]] = {}
        self.select: Tuple[str, str] = ('', '')
        self.relation_stack: List[Tuple[str, Tuple[str, str], Tuple[str, str]]] = []

    def evaluate_query(self, pql_ast_tree: Node) -> str:
        for node in pql_ast_tree.children:
            self.distribution_of_tasks(node)
        if self.select[0] == 'BOOLEAN':
            return str(self.results.get('BOOLEAN', False)).lower()
        if self.results.get(self.select[1], None) is None:
            if bool([value for value in self.results.values() if not value]):
                return 'none'
            if self.select[0] == 'STMT':
                return ', '.join(map(str, self.all_tables['statement'].get_all_statement_lines()))
            elif self.select[0] == 'PROCEDURE':
                return ', '.join(self.all_tables['proc'].get_all_proc_name())
            else:
                return ', '.join(map(str, self.all_tables['statement'].get_statement_line_by_type_name(self.select[0])))
        if len(self.results[self.select[1]]) == 0:
            return 'none'
        return ', '.join([str(element) for element in self.results[self.select[1]]])

    def distribution_of_tasks(self, root: Node) -> None:
        if root.node_type == 'RESULT':
            self.select = root.children[0].node_type, root.children[0].value
        elif root.node_type == 'WITH':
            for node in root.children:
                self.attr_analysis(node)
        elif root.node_type == 'PATTERN':
            for node in root.children:
                self.pattern_analysis(node)
        elif root.node_type == 'SUCH_THAT':
            for node in root.children:
                self.relation_preparation(node)
            self.check_stack_on_return()

    def pattern_analysis(self, pattern_node: Node) -> None:
        if pattern_node.node_type in ['PATTERN_WHILE', 'PATTERN_IF']:
            self.pattern_while_or_if(pattern_node)
        else:
            self.pattern_assign(pattern_node)

    def pattern_while_or_if(self, node: Node) -> None:
        if node.children[1].node_type in ['VARIABLE', 'EVERYTHING']:
            self.results[node.children[0].value] = self.all_tables['statement'] \
                .get_statement_line_by_type_name(node.children[0].node_type)
        else:
            self.results[node.children[0].value] = self.all_tables['statement'] \
                .get_statement_line_by_type_name_and_value(node.children[0].node_type, node.children[1].value)

        if self.results[node.children[0].value] and self.results.get('BOOLEAN', True) is True:
            self.results['BOOLEAN'] = True
        else:
            self.results['BOOLEAN'] = False

    def pattern_assign(self, node: Node) -> None:
        if node.children[1].node_type in ['VARIABLE', 'EVERYTHING']:
            self.results[node.children[0].value] = self.all_tables['statement'] \
                .get_statement_line_by_type_name(node.children[0].node_type)
        else:  # pobranie wszystkich lini gdy po lewej stronie rownania jest dana wartosć np. "t"
            self.results[node.children[0].value] = self.all_tables['statement'] \
                .get_statement_line_by_type_name_and_value(node.children[0].node_type, node.children[1].value)

        if self.results[node.children[0].value] and node.children[2].node_type == "EVERYTHING":
            self.pattern_wild_card(node.children[0].value, node.children[2])
        elif self.results[node.children[0].value]:
            # self.pattern_after_equals(node.children[0].value, node.children[2])
            pass

        if self.results[node.children[0].value] and self.results.get('BOOLEAN', True) is True:
            self.results['BOOLEAN'] = True
        else:
            self.results['BOOLEAN'] = False

    def pattern_wild_card(self, attr_name: str, node_expr: Node) -> None:
        if node_expr.children:
            search: SearchUtils = SearchUtils(self.ast_node)
            result: Set[int] = set()
            for line in self.results[attr_name]:
                search_node: Node = search.find_node_by_line_and_type_and_value(line, node_expr.children[0].node_type,
                                                                                node_expr.children[0].value)
                if search_node is not None:
                    if self.pattern_after_equals(search_node, node_expr.children[0])[0]:
                        result.add(int(line))
            self.results[attr_name] = result

    def pattern_after_equals(self, ast: Node, comparing_node: Node, parent: Node = Node()) -> Tuple[bool, bool]:
        """

        :param ast:
        :param comparing_node:
        :return: pierwszy bool oznacza czy jest identyczne wyrazenie a drugi czy jest to tylko czesc
        """
        if len(comparing_node.children) > len(ast.children):
            return False, False
        for index, child in enumerate(ast.children):
            if index < len(comparing_node.children):
                if ast.equals(comparing_node):
                    if not self.pattern_after_equals(child, comparing_node.children[index], ast)[0]:
                        return False, False
                else:
                    return False, False
            else:
                return False, False
        if ast.equals(comparing_node):
            if len(parent.children) == 2:
                return True, True
            return True, False
        else:
            return False, False

    def relation_preparation(self, relation: Node) -> None:
        # tworzenie tupli dwróch argumentów danej relacji
        first_argument: Tuple[str, str] = (relation.children[0].node_type, relation.children[0].value)
        second_argument: Tuple[str, str] = (relation.children[1].node_type, relation.children[1].value)

        # dodnaie do stosu relacji nowy element
        self.relation_stack.append((relation.node_type, first_argument, second_argument))

        # wybranie argumentu jesli typ argumentu to INTEGER, EVERYTHING, IDENT_QUOTE - zwraca str: np. 1, _, "x"
        # jesli typ argumentu jest IDENT - zwraca str(nazwa zmiennej) jesli na slowniku nie ma danego klucza
        # a jesli na slowniku jest klucz to zwroci nazwe zmienne i liste integerow
        first_argument_value: Union[str, Tuple[str, List[int]]] = self.choosing_an_argument(first_argument)
        second_argument_value: Union[str, Tuple[str, List[int]]] = self.choosing_an_argument(second_argument)

        self.execution_of_relation(relation.node_type, first_argument_value, second_argument_value)

    def choosing_an_argument(self, relation_argument: Tuple[str, str]) -> Union[
        str, Tuple[str, Set[int]], Tuple[str, str]]:
        if relation_argument[0] in ['INTEGER', 'EVERYTHING', 'IDENT_QUOTE']:
            return relation_argument[1]
        else:
            if self.results.get(relation_argument[1], None) is None:
                return relation_argument[1], relation_argument[0]
            else:
                if not self.results[relation_argument[1]]:
                    return relation_argument[1], relation_argument[0]
                else:
                    return relation_argument[1], self.results[relation_argument[1]]

    def execution_of_relation(self, node_type: str,
                              first_argument_value: Union[str, Tuple[str, List[int]]],
                              second_argument_value: Union[str, Tuple[str, List[int]]]) -> None:
        """
            wykona relacjie dla danych argumentów połączy dane zwracane
        :param node_type: nazwa relacji
        :param first_argument_value: pierwszy argument/argumenty relacji
        :param second_argument_value: drugi  argument/argumenty relacji
        """
        if type(first_argument_value) is tuple:
            if type(first_argument_value[1]) is set:  # pierwszy jest np. ('i2', [3,7]), ('s', [3,7,4,5])
                if type(second_argument_value) is tuple:
                    if type(second_argument_value[1]) is set:  # drugi jest np. ('i2', [3,7]), ('s', [3,7,4,5])
                        first_relation_result: Set[int] = set()
                        second_relation_result: Set[int] = set()
                        for first_argument in first_argument_value[1]:
                            for second_argument in second_argument_value[1]:
                                result: Union[Tuple[List[int], None], Tuple[List[str], None], Tuple[bool, None]] = \
                                    self.select_relation(node_type, str(first_argument), str(second_argument))
                                if result[0]:
                                    first_relation_result.add(first_argument)
                                    second_relation_result.add(second_argument)
                        if first_relation_result and self.results.get('BOOLEAN', True) is True:
                            self.results['BOOLEAN'] = True
                        else:
                            self.results['BOOLEAN'] = False
                        self.results[first_argument_value[0]] = first_relation_result
                        self.results[second_argument_value[0]] = second_relation_result
                    else:  # drugi jest np. ('i1','IF'), ('w','WHILE')
                        relation_result: Set[int] = set()
                        for argument in first_argument_value[1]:
                            result: Union[Tuple[List[int], None], Tuple[List[str], None]] = \
                                self.select_relation(node_type, str(argument), second_argument_value[1])
                            relation_result.update(result[0])
                        if relation_result and self.results.get('BOOLEAN', True) is True:
                            self.results['BOOLEAN'] = True
                        else:
                            self.results['BOOLEAN'] = False
                        self.results[second_argument_value[0]] = relation_result
                else:  # drugi argument jest np. 1, _, "x"
                    relation_result: Set[int] = set()
                    for argument in first_argument_value[1]:
                        result: Union[Tuple[List[int], None], Tuple[List[str], None], Tuple[bool, None]] = \
                            self.select_relation(node_type, str(argument), second_argument_value)
                        if result[0]:
                            relation_result.add(argument)
                    if relation_result and self.results.get('BOOLEAN', True) is True:
                        self.results['BOOLEAN'] = True
                    else:
                        self.results['BOOLEAN'] = False
                    self.results[first_argument_value[0]] = relation_result
            else:  # pierwszy jest np. ('i1','IF'), ('w','WHILE')
                if type(second_argument_value) is tuple:
                    if type(second_argument_value[1]) is set:  # drugi jest np. ('i2', [3,7]), ('s', [3,7,4,5])
                        relation_result: Set[int] = set()
                        for argument in second_argument_value[1]:
                            result: Union[Tuple[List[int], None], Tuple[List[str], None]] = \
                                self.select_relation(node_type, first_argument_value[1], str(argument))
                            relation_result.update(result[0])
                        if relation_result and self.results.get('BOOLEAN', True) is True:
                            self.results['BOOLEAN'] = True
                        else:
                            self.results['BOOLEAN'] = False
                        self.results[first_argument_value[0]] = relation_result
                    else:  # drugi jest np. ('i1','IF'), ('w','WHILE')
                        result: Union[Tuple[List[int], None], Tuple[List[str], None], Tuple[bool, None]] = \
                            self.select_relation(node_type, first_argument_value[1], second_argument_value[1])
                        if result[0] and result[1] and self.results.get('BOOLEAN', True) is True:
                            self.results['BOOLEAN'] = True
                        else:
                            self.results['BOOLEAN'] = False
                        self.results[first_argument_value[0]] = set(result[0])
                        self.results[second_argument_value[0]] = set(result[1])
                else:  # drugi argument jest np. 1, _, "x"
                    result: Union[Tuple[List[int], None], Tuple[List[str], None], Tuple[bool, None]] = \
                        self.select_relation(node_type, first_argument_value[1], second_argument_value)
                    if result[0] and self.results.get('BOOLEAN', True) is True:
                        self.results['BOOLEAN'] = True
                    else:
                        self.results['BOOLEAN'] = False
                    self.results[first_argument_value[0]] = set(result[0])
        else:  # pierwszy argument jest np. 1, _, "x"
            if type(second_argument_value) is tuple:
                if type(second_argument_value[1]) is set:  # drugi jest np. ('i2', [3,7]), ('s', [3,7,4,5])
                    relation_result: Set[int] = set()
                    for argument in second_argument_value[1]:
                        result: Union[Tuple[List[int], None], Tuple[List[str], None], Tuple[bool, None]] = \
                            self.select_relation(node_type, first_argument_value, str(argument))
                        if result[0]:
                            relation_result.add(argument)
                    if relation_result and self.results.get('BOOLEAN', True) is True:
                        self.results['BOOLEAN'] = True
                    else:
                        self.results['BOOLEAN'] = False
                    self.results[second_argument_value[0]] = relation_result
                else:  # drugi jest np. ('i1','IF'), ('w','WHILE')
                    result: Union[Tuple[List[int], None], Tuple[List[str], None], Tuple[bool, None]] = \
                        self.select_relation(node_type, first_argument_value, second_argument_value[1])
                    if result[0] and self.results.get('BOOLEAN', True) is True:
                        self.results['BOOLEAN'] = True
                    else:
                        self.results['BOOLEAN'] = False
                    self.results[second_argument_value[0]] = set(result[0])
            else:  # drugi argument jest np. 1, _, "x"
                result: Union[Tuple[List[int], None], Tuple[List[str], None], Tuple[bool, None]] = \
                    self.select_relation(node_type, first_argument_value, second_argument_value)
                if result[0] and self.results.get('BOOLEAN', True) is True:
                    self.results['BOOLEAN'] = True
                else:
                    self.results['BOOLEAN'] = False

    def select_relation(self, relation_type: str, first_argument: str, second_argument: str) -> \
            Union[Tuple[List[int], None], Tuple[List[str], None], Tuple[bool, None]]:

        if relation_type == 'MODIFIES':
            return ModifiesRelation(self.all_tables['modifies'], self.all_tables['var'],
                                    self.all_tables['statement'], self.all_tables['proc']) \
                .modifies(first_argument, second_argument)
        elif relation_type == 'USES':
            return UsesRelation(self.all_tables['uses'], self.all_tables['var'],
                                self.all_tables['statement'], self.all_tables['proc']) \
                .uses(first_argument, second_argument)
        elif relation_type == 'PARENT':
            return ParentRelation(self.all_tables['parent'], self.all_tables['statement']) \
                .parent(first_argument, second_argument)
        elif relation_type == 'PARENTT':
            return ParentRelation(self.all_tables['parent'], self.all_tables['statement']) \
                .parent_T(first_argument, second_argument)
        elif relation_type == 'FOLLOWS':
            return FollowsRelation(self.all_tables['follows'], self.all_tables['statement']) \
                .follows(first_argument, second_argument)
        elif relation_type == 'FOLLOWST':
            return FollowsRelation(self.all_tables['follows'], self.all_tables['statement']) \
                .follows_T(first_argument, second_argument)
        elif relation_type == 'CALLS':
            return CallsRelation(self.all_tables['calls'], self.all_tables['var'], self.all_tables['statement'],
                                 self.all_tables['proc']) \
                .calls(first_argument, second_argument)
        elif relation_type == 'CALLST':
            return CallsRelation(self.all_tables['calls'], self.all_tables['var'], self.all_tables['statement'],
                                 self.all_tables['proc']) \
                .calls_T(first_argument, second_argument)
        elif relation_type == 'NEXT':
            return NextRelation(self.all_tables['next'], self.all_tables['statement']) \
                .next(first_argument, second_argument)
        elif relation_type == 'NEXTT':
            return NextRelation(self.all_tables['next'], self.all_tables['statement']) \
                .next_T(first_argument, second_argument)

    def attr_analysis(self, attr_node: Node) -> None:
        if attr_node.children[1].node_type in ['INTEGER', 'IDENT_QUOTE']:
            self.results[attr_node.children[0].value] = set([attr_node.children[1].value])
        elif attr_node.children[1].node_type == 'CONSTANT':
            self.results[attr_node.children[0].value] = set(self.all_tables['const'].get_all_constant())
        else:
            if attr_node.children[0].node_type in ['CALL', 'PROCEDURE']:
                left: Set[str] = set(self.all_tables['proc'].get_all_proc_name())
            else:
                left: Set[str] = set(self.all_tables['var'].get_all_var_name())

            if attr_node.children[1].node_type in ['CALL', 'PROCEDURE']:
                right: Set[str] = set(self.all_tables['proc'].get_all_proc_name())
            else:
                right: Set[str] = set(self.all_tables['var'].get_all_var_name())

            self.results[attr_node.children[0].value] = left.intersection(right)

    def check_stack_on_return(self) -> None:
        while len(self.relation_stack) != 0:
            relation: Tuple[str, Tuple[str, str], Tuple[str, str]] = self.relation_stack.pop()
            self.execution_of_relation(relation[0],
                                       self.choosing_an_argument(relation[1]),
                                       self.choosing_an_argument(relation[2]))
