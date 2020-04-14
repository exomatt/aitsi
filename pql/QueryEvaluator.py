from typing import List, Union, Dict, Tuple

from aitsi_parser.CallsTable import CallsTable
from aitsi_parser.FollowsTable import FollowsTable
from aitsi_parser.ModifiesTable import ModifiesTable
from aitsi_parser.ParentTable import ParentTable
from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.UsesTable import UsesTable
from aitsi_parser.VarTable import VarTable
from pql.Node import Node
from pql.relations.CallsRelation import CallsRelation
from pql.relations.FollowsRelation import FollowsRelation
from pql.relations.ModifiesRelation import ModifiesRelation
from pql.relations.ParentRelation import ParentRelation
from pql.relations.UsesRelation import UsesRelation


class QueryEvaluator:

    def __init__(self, code_ast_tree: Node, all_tables: Dict[str,
                                                             Union[VarTable,
                                                                   ProcTable,
                                                                   UsesTable,
                                                                   ParentTable,
                                                                   ModifiesTable,
                                                                   FollowsTable,
                                                                   CallsTable,
                                                                   StatementTable]]) -> None:
        self.code_ast_tree: Node = code_ast_tree
        self.all_tables: Dict[str, Union[VarTable,
                                         ProcTable,
                                         UsesTable,
                                         ParentTable,
                                         ModifiesTable,
                                         FollowsTable,
                                         CallsTable,
                                         StatementTable]] = all_tables
        self.results: Dict[str, Union[bool, List[str], List[int]]] = {}
        self.select: Tuple[str, str] = ('', '')
        self.parameters_with: Dict[str, Tuple[str, Dict[str, str]]] = {}
        self.and_flag = False
        self.relation_stack: List[Tuple[str, Tuple[str, str], Tuple[str, str]]] = []

    def evaluate_query(self, pql_ast_tree: Node) -> str:
        for node in pql_ast_tree.children:
            self.distribution_of_tasks(node)
        return ', '.join([str(element) for element in self.results])  # todo teraz zle poprawa

    def distribution_of_tasks(self, root: Node) -> None:
        if root.node_type == 'RESULT':
            self.select = root.children[0].node_type, root.children[0].value
        elif root.node_type == 'SUCH_THAT':
            for node in root.children:
                self.relation_preparation(node)
        elif root.node_type == 'WITH':
            for node in root.children:
                self.attr_analysis(node)

    def relation_preparation(self, relation: Node) -> None:
        # tworzenie tupli dwróch argumentów danej relacji
        first_argument: Tuple[str, str] = (relation.children[0].node_type, relation.children[0].value)
        second_argument: Tuple[str, str] = (relation.children[1].node_type, relation.children[1].value)

        # dodnaie do stosu relacji nowy element
        self.relation_stack.append((relation.node_type, first_argument, second_argument))

        # wybranie argumentu jesli typ argumentu to INTEGER, EVERYTHING, IDENT_QUOTE - zwraca str: np, 1, _, "x"
        # jesli typ argumentu jest IDENT - zwraca str(nazwa zmiennej) jesli na slowniku nie ma danego klucza
        # a jesli na slowniku jest klucz to zwroci liste integerow
        first_argument_value: Union[str, Tuple[str, List[int]]] = self.choosing_an_argument(first_argument)
        second_argument_value: Union[str, Tuple[str, List[int]]] = self.choosing_an_argument(second_argument)

        self.execution_of_relation(relation.node_type, first_argument_value, second_argument_value)

    def choosing_an_argument(self, relation_argument: Tuple[str, str]) -> Union[str, Tuple[str, List[int]]]:
        if relation_argument[0] in ['INTEGER', 'EVERYTHING', 'IDENT_QUOTE']:
            return relation_argument[1]
        else:
            if self.results.get(relation_argument[1], None) is None:
                return relation_argument[0]
            return relation_argument[0], self.results.get(relation_argument[1], None)

    def execution_of_relation(self, node_type: str,
                              first_argument_value: Union[str, Tuple[str, List[int]]],
                              second_argument_value: Union[str, Tuple[str, List[int]]]) -> None:
        """
            wykona relacjie dla danych argumentów połączy dane zwracane
        :param node_type: nazwa relacji
        :param first_argument_value: pierwszy argument/argumenty relacji
        :param second_argument_value: drugi  argument/argumenty relacji
        """
        if type(first_argument_value) is tuple:  # pierwszy argument to tupel z lista wierszy w kodzie
            if type(second_argument_value) is tuple:  # drugi argument to tupel z lista wierszy w kodzie
                pass
            else:  # drugi argument jest typem stetmenta
                pass
        else:  # pierwszy argument jest typem stetmenta
            if type(second_argument_value) is tuple:  # drugi argument to tupel z lista wierszy w kodzie
                pass
            else:  # drugi argument jest typem stetmenta
                self.select_relation(node_type, first_argument_value, second_argument_value)

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

    def adding_relation_result_to_result(self, relation_result: Union[
        Tuple[List[int], None], Tuple[List[str], None], Tuple[bool, None]], relation_node: Node):
        """
        łączenie danych przychodzacych z relacji w jedną odpowiedź
        :param relation_result: odpowiedz z reacji
        :param relation_node: analizowny Node relacji
        """
        # TODO zalkończyc program jesli rezultat z relacji jest nullem
        if relation_result[1] is not None:  # odpowedz z relacji jest ((lista || bool), (lista || bool))
            if self.select[1] == relation_node.children[0].value:  # zmienna w select jest pierwszym argumentem relacji

                if self.results is not None:  # wynik ostateczny ma juz wyniki z poprzednich relacji
                    self.results = list(set(self.results).intersection(set(relation_result[0])))
                    # TODO zalkończyc program jesli rezultat jest nullem
                else:  # wynik ostateczny jest None
                    self.results = relation_result[0]
                    # TODO zalkończyc program jesli rezultat jest nullem
            elif self.select[1] == relation_node.children[1].value:  # zmienna w select jest drugim argumentem relacji
                if self.results is not None:  # wynik ostateczny ma juz wyniki z poprzednich relacji
                    self.results = list(set(self.results).intersection(set(relation_result[1])))
                    # TODO zalkończyc program jesli rezultat jest nullem
                else:  # wynik ostateczny jest None
                    self.results = relation_result[1]
                    # TODO zalkończyc program jesli rezultat jest nullem
        else:  # odpowedz z relacji jest (lista, None)
            if self.results is not None:  # wynik ostateczny ma juz wyniki z poprzednich relacji
                self.results = list(set(self.results).intersection(set(relation_result[0])))
                # TODO zalkończyc program jesli rezultat jest nullem
            else:  # wynik ostateczny jest None
                self.results = relation_result[0]
                # TODO zalkończyc program jesli rezultat jest nullem

    def attr_analysis(self, attr_node: Node) -> None:
        self.parameters_with[attr_node.children[0].value] = (
            (attr_node.children[0].node_type, self.right_side(attr_node.children[1])))

    def right_side(self, right_node: Node) -> Dict[str, str]:
        return {'type': right_node.node_type, 'variable_name': right_node.value}
