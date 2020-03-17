from typing import Union, List, Optional, Set

from pql.Node import Node
from pql.utils.SearchUtils import SearchUtils


class ModifiesRelation:
    def __init__(self, ast_tree: Node) -> None:
        super().__init__()
        self.ast_tree: Node = ast_tree

    def modifies(self, param_first: str, param_second: str, ) -> Union[List[str], List[int]]:
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        if param_first.isdigit():
            if param_second == '_':
                # p1 jest liczba, a p2 zmienna wild card  np. '_' zwraca nazwe zmiennej modyfikowanej w tej lini w liscie lub pusta liste
                node: Optional[Node] = search_utils.find_node_by_line(int(param_first))
                if node is None:
                    return []
                elif node.node_type == 'ASSIGN':
                    for children in node.children:
                        if children.node_type == 'NAME':
                            return [children.line]
                return []
            elif param_second == 'VARIABLE':
                # p1 jest liczba, a p2 zmienna variable v czyli   np. 'VARIABLE' Modifies('3',v) zwraca nazwe zmiennej modyfikowanej w tej lini w liscie lub pusta liste
                node: Optional[Node] = search_utils.find_node_by_line(int(param_first))
                if node is None:
                    return []
                elif node.node_type == 'ASSIGN':
                    for children in node.children:
                        if children.node_type == 'NAME':
                            return [children.value]
                return []
            else:
                # p1 jest liczba, a p2 zmienna variable np. 'x'
                # zwraca numer lini  jezeli w danej linii zachodzi modyfikacja zmiennej w innym przypadku []
                node: Optional[Node] = search_utils.find_node_by_line(int(param_first))
                if node is None:
                    return []
                elif node.node_type == 'ASSIGN':
                    for children in node.children:
                        if children.node_type == 'NAME' and children.value == param_second:
                            return [children.line]  # fixme dodc ze tylko dziecko po lewej stronie
                return []

        elif param_first == '_':
            if param_second == '_':
                # p1 jest '_', a p2 zmienna variable np.  variable v Modifies('_', '_') zwraca numery lini  gdzie jest cos modyfikowane
                stmt_list = self._get_all_stmt_list_in_procedure(search_utils)
                result_lines: List[int] = []
                for stmt in stmt_list:
                    if stmt.node_type == 'ASSIGN':
                        for children in stmt.children:
                            if children.node_type == 'NAME':
                                result_lines.append(children.line)

                return result_lines
                pass
            elif param_second == 'VARIABLE':
                # p1 jest '_', a p2 zmienna variable np.  variable v Modifies('_', v) zwraca nazwy zmiennych   ktore sa modyfikowane gdziekolwiek
                nodes_by_type: List[Node] = []
                nodes_by_type.extend(search_utils.find_node_by_type('IF'))
                nodes_by_type.extend(search_utils.find_node_by_type('WHILE'))
                nodes_by_type.extend(search_utils.find_node_by_type('PROCEDURE'))
                stmt_list: List[Node] = []
                return self._get_all_modified_variable_in_stmtlist(nodes_by_type, stmt_list)
            else:
                # p1 jest '_', a p2 zmienna variable np. 'x' zwraca numery lini    gdzie jest modyfikowanea zmienna o nazwie x
                stmt_list = self._get_all_stmt_list_in_procedure(search_utils)
                result_lines: List[int] = []
                for stmt in stmt_list:
                    if stmt.node_type == 'ASSIGN':
                        for children in stmt.children:
                            if children.node_type == 'NAME' and children.value.strip() == param_second:
                                result_lines.append(children.line)
                return result_lines
        else:
            if param_second == '_':
                # p1 jest stmt np 'IF', a p2  '_'   przypadek skrajny Modifies('IF',_) zwraca linie gdzie cokolwiek jest modyfikowane
                stmt_list = self._get_stmt_list_by_param(param_first, search_utils)
                result_lines: List[int] = []
                for stmt in stmt_list:
                    if stmt.node_type == 'ASSIGN':
                        for children in stmt.children:
                            if children.node_type == 'NAME':
                                result_lines.append(children.line)
                return result_lines
            elif param_second == 'VARIABLE':
                # wedlug handbooka to kiedy jest if i while to zwracamy wszystkie modyfikowane  zmienne
                # np. 'VARIABLE' Modifies('IF',v)
                nodes_by_type: List[Node] = []
                nodes_by_type.extend(search_utils.find_node_by_type(param_first))
                stmt_list: List[Node] = []
                return self._get_all_modified_variable_in_stmtlist(nodes_by_type, stmt_list)
            else:
                # p1 jest stmt np 'IF', a p2 zmienna variable np. 'x' zwracamy numer lini modyfikacji zmiennej 'x'
                stmt_list = self._get_stmt_list_by_param(param_first, search_utils)
                result_lines: List[int] = []
                for stmt in stmt_list:
                    if stmt.node_type == 'ASSIGN':
                        for children in stmt.children:
                            if children.node_type == 'NAME' and children.value.strip() == param_second:
                                result_lines.append(children.line)
                return result_lines

    def _get_stmt_list_by_param(self, param_first, search_utils) -> List[Node]:
        nodes_by_type: List[Node] = []
        nodes_by_type.extend(search_utils.find_node_by_type(param_first))
        stmt_list: List[Node] = []
        for node in nodes_by_type:
            for children in node.children:
                if children.node_type == 'STMT_LIST':
                    stmt_list.extend(children.children)
        return stmt_list

    def _get_all_modified_variable_in_stmtlist(self, nodes_by_type, stmt_list) -> List[str]:
        result_lines: Set[str] = set()
        for node in nodes_by_type:
            for children in node.children:
                if children.node_type == 'STMT_LIST':
                    stmt_list.extend(children.children)
        for stmt in stmt_list:
            if stmt.node_type == 'ASSIGN':
                for children in stmt.children:
                    if children.node_type == 'NAME':
                        result_lines.add(children.value.strip())
        return list(result_lines)

    def _get_all_stmt_list_in_procedure(self, search_utils) -> List[Node]:
        nodes_by_type: List[Node] = []
        nodes_by_type.extend(search_utils.find_node_by_type('IF'))
        nodes_by_type.extend(search_utils.find_node_by_type('WHILE'))
        nodes_by_type.extend(search_utils.find_node_by_type('PROCEDURE'))
        stmt_list: List[Node] = []

        for node in nodes_by_type:
            for children in node.children:
                if children.node_type == 'STMT_LIST':
                    stmt_list.extend(children.children)
        return stmt_list
