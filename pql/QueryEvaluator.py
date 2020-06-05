import itertools
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
from pql.Graph import Graph
from pql.Node import Node
from pql.ResultsTable import ResultsTable
from pql.relations.CallsRelation import CallsRelation
from pql.relations.CallsTRelation import CallsTRelation
from pql.relations.FollowsRelation import FollowsRelation
from pql.relations.FollowsTRelation import FollowsTRelation
from pql.relations.ModifiesRelation import ModifiesRelation
from pql.relations.NextRelation import NextRelation
from pql.relations.NextTRelation import NextTRelation
from pql.relations.ParentRelation import ParentRelation
from pql.relations.ParentTRelation import ParentTRelation
from pql.relations.Pattern import Pattern
from pql.relations.UsesRelation import UsesRelation
from pql.relations.With import With


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
        self.results_table: ResultsTable = ResultsTable()
        self.relation_index_stack: Set[str] = set()
        # stopien ograniczenia
        # 1.stala liczba
        # 1.staly nazwa
        # 2.Zmienna
        # 3.wild card
        #
        # 1.Next
        # 2.Follows
        # 3.Calls
        # 4.Parent
        # 5.Modifies
        # 6.Uses
        # 7.Parent*
        # 8.Follows*
        # 9.Calls*
        # 10.Next*
        self.degree_of_restriction = {
            'INTEGER': 1,
            'IDENT_QUOTE': 1,
            'STMT': 2,
            'WHILE': 2,
            'ASSIGN': 2,
            'VARIABLE': 2,
            'CONSTANT': 2,
            'PROCEDURE': 2,
            'PROG_LINE': 2,
            'CALL': 2,
            'IF': 2,
            'EVERYTHING': 3,
            'NEXT': 1,
            'FOLLOWS': 2,
            'CALLS': 3,
            'PARENT': 4,
            'MODIFIES': 5,
            'USES': 6,
            'PARENTT': 7,
            'FOLLOWST': 8,
            'CALLST': 9,
            'NEXTT': 10,
        }
        self.relation: Dict[str, Union[
            ModifiesRelation, FollowsRelation, FollowsTRelation, ParentRelation, ParentTRelation, UsesRelation,
            NextRelation, NextTRelation, CallsRelation, CallsTRelation, Pattern, With]] = {
            'MODIFIES': ModifiesRelation(self.all_tables['modifies'], self.all_tables['var'],
                                         self.all_tables['statement'], self.all_tables['proc']),
            'USES': UsesRelation(self.all_tables['uses'], self.all_tables['var'],
                                 self.all_tables['statement'], self.all_tables['proc']),
            'PARENT': ParentRelation(self.all_tables['parent'], self.all_tables['statement']),
            'PARENTT': ParentTRelation(self.all_tables['parent'], self.all_tables['statement']),
            'FOLLOWS': FollowsRelation(self.all_tables['follows'], self.all_tables['statement']),
            'FOLLOWST': FollowsTRelation(self.all_tables['follows'], self.all_tables['statement']),
            'CALLS': CallsRelation(self.all_tables['calls'], self.all_tables['var'], self.all_tables['statement'],
                                   self.all_tables['proc']),
            'CALLST': CallsTRelation(self.all_tables['calls'], self.all_tables['var'], self.all_tables['statement'],
                                     self.all_tables['proc']),
            'NEXT': NextRelation(self.all_tables['next'], self.all_tables['statement']),
            'NEXTT': NextTRelation(self.all_tables['next'], self.all_tables['statement']),
            'PATTERN': Pattern(ast_node, self.all_tables['statement']),
            'WITH': With(self.all_tables)
        }

    def evaluate_query(self, pql_ast_tree: Node) -> str:
        for node in pql_ast_tree.children:
            self.distribution_of_tasks(node)

        return self.results_table.get_select(self.all_tables)

    def distribution_of_tasks(self, root: Node) -> None:
        if root.node_type == 'RESULT':
            self.select = root.children[0].node_type, root.children[0].value
            self.results_table.select = root.children[0].node_type, root.children[0].value
        elif root.node_type == 'WITH':
            for node in root.children:
                self.attr_analysis(node)
        elif root.node_type == 'PATTERN':
            for node in root.children:
                self.pattern(node)
        elif root.node_type == 'SUCH_THAT':
            if len(root.children) > 1:
                root.children.sort(key=self.relation_sort)
                root.children = list(set(root.children))
                root.children.sort(key=self.relation_sort)
                for node in root.children:
                    self.relation_preparation(node)
                self.final_check()
                if self.check_if_relations_constains_cycle(root.children):
                    self.check_relations_when_we_got_cycle(root.children)
            else:
                self.relation_preparation(root.children[0])

    def check_if_relations_constains_cycle(self, relations: List[Node]) -> bool:
        index: int = 0
        relations_graph_map = {}
        for relation in relations:
            if relation.children[0].node_type not in ['INTEGER', 'EVERYTHING', 'IDENT_QUOTE'] and relation.children[
                1].node_type not in ['INTEGER', 'EVERYTHING', 'IDENT_QUOTE']:
                if relation.children[0].value not in relations_graph_map:
                    relations_graph_map[relation.children[0].value] = index
                    index += 1
                if relation.children[1].value not in relations_graph_map:
                    relations_graph_map[relation.children[1].value] = index
                    index += 1

        graph: Graph = Graph(index)
        for relation in relations:
            if relation.children[0].node_type not in ['INTEGER', 'EVERYTHING', 'IDENT_QUOTE'] \
                    and relation.children[1].node_type not in ['INTEGER', 'EVERYTHING', 'IDENT_QUOTE']:
                graph.addEdge(relations_graph_map[relation.children[0].value],
                              relations_graph_map[relation.children[1].value])
        return graph.isCyclic()

    def check_relations_when_we_got_cycle(self, relations: List[Node]):
        synonyms_names: List[str] = self.results_table.table.columns.tolist()
        synonyms_names.remove('BOOLEAN')
        synonyms_names.remove('CONST')
        mapa: Dict[str, int] = {}
        for index, sn in enumerate(synonyms_names):
            mapa[sn] = index

        zmienna = [self.results_table.get_final_result(sn) for sn in synonyms_names]
        wyniki: Dict[str, Union[Set[str], Set[int]]] = {}
        for k in mapa:
            wyniki[k] = set()

        for x in itertools.product(*zmienna):
            passed_test = True
            for relation in relations:
                relation_result = self.relation[relation.node_type].value_from_set_and_value_from_set(
                    x[mapa.get(relation.children[0].value)], x[mapa.get(relation.children[1].value)])
                if not relation_result:
                    passed_test = False
                    break

            if passed_test:
                for k in mapa:
                    wyniki[k].add(x[mapa[k]])

        for k in mapa:
            self.results_table.update_results('final', k, wyniki[k])

    def relation_sort(self, relation: Node) -> int:
        return self.degree_of_restriction[relation.node_type] \
               + self.degree_of_restriction[relation.children[0].node_type] \
               + self.degree_of_restriction[relation.children[1].node_type]

    def pattern(self, pattern_node: Node) -> None:
        self.results_table.set_results(pattern_node.children[0].value, pattern_node.children[0].node_type)
        self.results_table.update_results('PATTERN',
                                          pattern_node.children[0].value,
                                          self.relation['PATTERN'].execute(pattern_node))

    def relation_preparation(self, relation: Node) -> None:
        # tworzenie tupli dwróch argumentów danej relacji
        first_argument: Tuple[str, str] = (relation.children[0].node_type, relation.children[0].value)
        second_argument: Tuple[str, str] = (relation.children[1].node_type, relation.children[1].value)

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
            self.results_table.set_results(relation_argument[1], relation_argument[0])
            if self.results_table.get_final_result(relation_argument[1]) is None:
                if relation_argument[0] == 'PROG_LINE':
                    return relation_argument[1], 'STMT'
                return relation_argument[1], relation_argument[0]
            else:
                if not self.results_table.get_final_result(relation_argument[1]):
                    if relation_argument[0] == 'PROG_LINE':
                        return relation_argument[1], 'STMT'
                    return relation_argument[1], relation_argument[0]
                else:
                    return relation_argument[1], self.results_table.get_final_result(relation_argument[1])

    def execution_of_relation(self, node_type: str,
                              first_argument_value: Union[str, Tuple[str, Set[int]]],
                              second_argument_value: Union[str, Tuple[str, Set[int]]]) -> None:
        """
            wykona relacjie dla danych argumentów połączy dane zwracane
        :param node_type: nazwa relacji
        :param first_argument_value: pierwszy argument/argumenty relacji
        :param second_argument_value: drugi  argument/argumenty relacji
        """
        relation_index: str = ''
        if type(first_argument_value) is tuple:
            if type(first_argument_value[1]) is set:  # pierwszy jest np. ('i2', [3,7]), ('s', [3,7,4,5])
                if type(second_argument_value) is tuple:
                    if type(second_argument_value[1]) is set:  # drugi jest np. ('i2', [3,7]), ('s', [3,7,4,5])
                        relation_index = f"{node_type}_{first_argument_value[0]}_{second_argument_value[0]}"
                        first_relation_result: Set[int] = set()
                        second_relation_result: Set[int] = set()
                        for first_argument in first_argument_value[1]:
                            for second_argument in second_argument_value[1]:
                                result: bool = self.relation[node_type].value_from_set_and_value_from_set(
                                    str(first_argument), str(second_argument))
                                if result:
                                    first_relation_result.add(first_argument)
                                    second_relation_result.add(second_argument)
                        self.results_table.update_results(relation_index,
                                                          first_argument_value[0],
                                                          first_relation_result)
                        self.results_table.update_results(relation_index,
                                                          second_argument_value[0],
                                                          second_relation_result)
                    else:  # drugi jest np. ('i1','IF'), ('w','WHILE'), ('v','VARIABLE')
                        relation_index = f"{node_type}_{first_argument_value[0]}_{second_argument_value[0]}"
                        relation_result: Set[int] = set()
                        first_argument_relation_result: Set[int] = set()
                        for argument in first_argument_value[1]:
                            result: Union[List[int], List[str]] = \
                                self.relation[node_type].value_from_set_and_not_initialized_set(str(argument),
                                                                                                second_argument_value[
                                                                                                    1])
                            if result:
                                relation_result.update(result)
                                first_argument_relation_result.add(argument)
                        self.results_table.update_results(relation_index,
                                                          first_argument_value[0],
                                                          first_argument_relation_result)
                        self.results_table.update_results(relation_index,
                                                          second_argument_value[0],
                                                          relation_result)
                else:  # drugi argument jest np. 1, _, "x"
                    relation_index = f"{node_type}_{first_argument_value[0]}_CONST"
                    relation_result: Set[int] = set()
                    for argument in first_argument_value[1]:
                        result: bool = \
                            self.relation[node_type].value_from_set_and_value_from_query(str(argument),
                                                                                         second_argument_value)
                        if result:
                            relation_result.add(argument)
                    self.results_table.update_results(relation_index,
                                                      first_argument_value[0],
                                                      relation_result)
                    self.results_table.update_results(relation_index,
                                                      'CONST',
                                                      second_argument_value)
            else:  # pierwszy jest np. ('i1','IF'), ('w','WHILE')
                if type(second_argument_value) is tuple:
                    if type(second_argument_value[1]) is set:  # drugi jest np. ('i2', [3,7]), ('s', [3,7,4,5])
                        relation_index = f"{node_type}_{first_argument_value[0]}_{second_argument_value[0]}"
                        relation_result_first_argument: Set[int] = set()
                        relation_result_second_argument: Union[Set[int], Set[str]] = set()
                        for argument in second_argument_value[1]:
                            result: Union[List[int], List[str]] = \
                                self.relation[node_type].not_initialized_set_and_value_from_set(first_argument_value[1],
                                                                                                str(argument))
                            result = list(filter(lambda line: line is not None, result))
                            if result:
                                relation_result_first_argument.update(result)
                                relation_result_second_argument.add(argument)
                        self.results_table.update_results(
                            relation_index,
                            first_argument_value[0],
                            relation_result_first_argument)
                        self.results_table.update_results(
                            relation_index,
                            second_argument_value[0],
                            relation_result_second_argument)
                    else:  # drugi jest np. ('i1','IF'), ('w','WHILE')
                        relation_index = f"{node_type}_{first_argument_value[0]}_{second_argument_value[0]}"
                        result: Union[Tuple[List[int], List[int]],
                                      Tuple[List[str], List[str]],
                                      Tuple[List[int], List[str]],
                                      Tuple[List[str], List[int]]] = \
                            self.relation[node_type].not_initialized_set_and_not_initialized_set(
                                first_argument_value[1], second_argument_value[1])
                        self.results_table.update_results(relation_index,
                                                          first_argument_value[0],
                                                          set(result[0]))
                        self.results_table.update_results(relation_index,
                                                          second_argument_value[0],
                                                          set(result[1]))
                else:  # drugi argument jest np. 1, _, "x"
                    relation_index = f"{node_type}_{first_argument_value[0]}_CONST"
                    result: Union[List[int], List[str]] = \
                        self.relation[node_type].not_initialized_set_and_value_from_query(first_argument_value[1],
                                                                                          second_argument_value)
                    self.results_table.update_results(relation_index,
                                                      first_argument_value[0],
                                                      set(result))
                    self.results_table.update_results(relation_index,
                                                      'CONST',
                                                      second_argument_value)
        else:  # pierwszy argument jest np. 1, _, "x"
            if type(second_argument_value) is tuple:
                if type(second_argument_value[1]) is set:  # drugi jest np. ('i2', [3,7]), ('s', [3,7,4,5])
                    relation_index = f"{node_type}_CONST_{second_argument_value[0]}"
                    relation_result: Union[Set[int], Set[str]] = set()
                    for argument in second_argument_value[1]:
                        result: bool = self.relation[node_type].value_from_query_and_value_from_set(
                            first_argument_value, str(argument))
                        if result:
                            relation_result.add(argument)
                    self.results_table.update_results(relation_index,
                                                      'CONST',
                                                      first_argument_value)
                    self.results_table.update_results(relation_index,
                                                      second_argument_value[0],
                                                      relation_result)
                else:  # drugi jest np. ('i1','IF'), ('w','WHILE')
                    relation_index = f"{node_type}_CONST_{second_argument_value[0]}"
                    result: Union[List[int], List[str]] = \
                        self.relation[node_type].value_from_query_and_not_initialized_set(first_argument_value,
                                                                                          second_argument_value[1])
                    self.results_table.update_results(relation_index,
                                                      'CONST',
                                                      first_argument_value)
                    self.results_table.update_results(relation_index,
                                                      second_argument_value[0],
                                                      set(result))
            else:  # drugi argument jest np. 1, _, "x"
                result: bool = \
                    self.relation[node_type].value_from_query_and_value_from_query(first_argument_value,
                                                                                   second_argument_value)
                if not result:
                    raise Exception()
                self.results_table.table.at['final', 'BOOLEAN'] = result

        if type(first_argument_value) is tuple:
            relations: List[str] = [relation for relation in
                                    self.results_table.get_relations(first_argument_value[0]) if
                                    relation not in ['type', 'final', 'PATTERN', 'WITH', relation_index,
                                                     *self.relation_index_stack] and 'CONST' not in relation]
            if relations:
                self.relation_index_stack.add(relation_index)
                for relation in relations:
                    relation_data = relation.split('_')
                    if relation_data[2] == first_argument_value[0]:
                        first_argument: Union[Tuple[str, Set[int]], Tuple[str, Set[str]]] = (
                            relation_data[1], self.results_table.table.at['type', relation_data[1]])
                        second_argument: Tuple[str, str] = (
                            relation_data[2], self.results_table.table.at['final', relation_data[2]])
                    elif relation_data[2] == second_argument_value[0]:
                        self.check_two_relation_with_the_same_argument(relation, relation_index)
                        first_argument: Union[Tuple[str, Set[int]], Tuple[str, Set[str]]] = (
                            relation_data[1], self.results_table.table.at['final', relation_data[1]])
                        second_argument: Union[Tuple[str, Set[int]], Tuple[str, Set[str]]] = (
                            relation_data[2], self.results_table.table.at['final', relation_data[2]])
                    else:
                        first_argument: Tuple[str, str] = (
                            relation_data[1], self.results_table.table.at['final', relation_data[1]])
                        second_argument: Union[Tuple[str, Set[int]], Tuple[str, Set[str]]] = (
                            relation_data[2], self.results_table.table.at['type', relation_data[2]])
                    self.execution_of_relation(relation_data[0], first_argument, second_argument)
                self.relation_index_stack.remove(relation_index)

        if type(second_argument_value) is tuple:
            relations: List[str] = [relation for relation in
                                    self.results_table.get_relations(second_argument_value[0]) if
                                    relation not in ['type', 'final', 'PATTERN', 'WITH', relation_index,
                                                     *self.relation_index_stack] and 'CONST' not in relation]
            if relations:
                self.relation_index_stack.add(relation_index)
                for relation in relations:
                    relation_data = relation.split('_')
                    if relation_data[1] == second_argument_value[0]:
                        first_argument: Union[Tuple[str, Set[int]], Tuple[str, Set[str]]] = (
                            relation_data[1], self.results_table.table.at['final', relation_data[1]])
                        second_argument: Tuple[str, str] = (
                            relation_data[2], self.results_table.table.at['type', relation_data[2]])
                    elif relation_data[1] == first_argument_value[0]:
                        first_argument: Union[Tuple[str, Set[int]], Tuple[str, Set[str]]] = (
                            relation_data[1], self.results_table.table.at['final', relation_data[1]])
                        second_argument: Union[Tuple[str, Set[int]], Tuple[str, Set[str]]] = (
                            relation_data[2], self.results_table.table.at['final', relation_data[2]])
                    else:
                        first_argument: Tuple[str, str] = (
                            relation_data[1], self.results_table.table.at['type', relation_data[1]])
                        second_argument: Union[Tuple[str, Set[int]], Tuple[str, Set[str]]] = (
                            relation_data[2], self.results_table.table.at['final', relation_data[2]])
                    self.execution_of_relation(relation_data[0], first_argument, second_argument)
                self.relation_index_stack.remove(relation_index)
        # print('Here')

    def attr_analysis(self, attr_node: Node) -> None:
        self.results_table.set_results(attr_node.children[0].value, attr_node.children[0].node_type)
        self.results_table.update_results('WITH',
                                          attr_node.children[0].value,
                                          self.relation['WITH'].execute(attr_node))

    def final_check(self):
        relations: List[str] = [relation for relation in
                                self.results_table.table.index.tolist() if
                                relation not in ['type', 'final', 'PATTERN', 'WITH'] and 'CONST' not in relation]
        for relation in relations:
            relation_data = str(relation).split('_')
            if self.results_table.table.at['final', relation_data[2]] != self.results_table.table.at[
                relation, relation_data[2]] \
                    or self.results_table.table.at['final', relation_data[1]] != self.results_table.table.at[
                relation, relation_data[1]]:
                first_argument: Union[Tuple[str, Set[int]], Tuple[str, Set[str]]] = (
                    relation_data[1], self.results_table.table.at['final', relation_data[1]])
                second_argument: Union[Tuple[str, Set[int]], Tuple[str, Set[str]]] = (
                    relation_data[2], self.results_table.table.at['final', relation_data[2]])
                self.execution_of_relation(relation_data[0], first_argument, second_argument)

    def check_two_relation_with_the_same_argument(self, first_relation: str, second_relation: str):
        first_relation_data: List[str] = first_relation.split('_')
        second_relation_data: List[str] = second_relation.split('_')
        results_final: Tuple[Union[Set[str], Set[int]], Union[Set[str], Set[int]]] = (
            self.results_table.table.at['final', first_relation_data[1]],
            self.results_table.table.at['final', first_relation_data[2]])
        results: Tuple[Union[Set[str], Set[int]], Union[Set[str], Set[int]]] = (set(), set())
        for first_argument in results_final[0]:
            for second_argument in results_final[1]:
                if self.relation[first_relation_data[0]] \
                        .value_from_set_and_value_from_set(str(first_argument), second_argument) and \
                        self.relation[second_relation_data[0]] \
                                .value_from_set_and_value_from_set(str(first_argument), second_argument):
                    results[0].add(first_argument)
                    results[1].add(second_argument)
        self.results_table.update_results(first_relation, first_relation_data[1], results[0])
        self.results_table.update_results(second_relation, first_relation_data[1], results[0])
        self.results_table.update_results(second_relation, first_relation_data[2], results[1])
        self.results_table.update_results(first_relation, first_relation_data[2], results[1])
