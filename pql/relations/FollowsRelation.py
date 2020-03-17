from typing import List

from pql.Node import Node
from pql.utils.SearchUtils import SearchUtils


class FollowsRelation:
    def __init__(self, ast_tree: Node) -> None:
        self.ast_tree: Node = ast_tree

    def follows(self, param_first: str, param_second: str) -> List[int]:
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        list_parents: List[Node] = search_utils.find_node_by_type('STMT_LIST')
        result: List[int] = []
        if param_first.isdigit():
            if param_second.isdigit():
                # p1 i p2 sa liczbami
                for parent in list_parents:
                    for index in range(len(parent.children)):
                        if parent.children[index].line == int(param_first):
                            if parent.children[index + 1].line == int(param_second):
                                return [int(param_first), int(param_second)]
                            else:
                                return []
            else:
                # p1 jest liczba, a p2 nie
                for parent in list_parents:
                    for index in range(len(parent.children)):
                        if parent.children[index].line == int(param_first):
                            if parent.children[index + 1].node_type == param_second:
                                result.append(parent.children[index + 1].line)
                            if param_second == '_' and parent.children[index + 1].node_type in ['WHILE', 'ASSIGN', 'IF',
                                                                                                'CALL']:
                                result.append(parent.children[index + 1].line)

                return result
        else:
            if param_second.isdigit():
                # p1 nie jest liczba, a p2 jest liczba
                for parent in list_parents:
                    for index in range(len(parent.children)):
                        if parent.children[index].line == int(param_second):
                            if index - 1 > -1:
                                if parent.children[index - 1].node_type == param_first:
                                    result.append(parent.children[index - 1].line)
                                if param_first == '_' and parent.children[index - 1].node_type in ['WHILE', 'ASSIGN',
                                                                                                   'IF', 'CALL']:
                                    result.append(parent.children[index - 1].line)

                return result

            else:
                # p1 i p2 nie sa liczbami
                for parent in list_parents:
                    for index in range(len(parent.children)):
                        if parent.children[index].node_type == param_first:
                            if len(parent.children) > index+1:
                                if parent.children[index + 1].node_type == param_second:
                                    result.append(parent.children[index].line)
                                    result.append(parent.children[index + 1].line)
                                if param_second == '_' and parent.children[index + 1].node_type in ['WHILE', 'ASSIGN', 'IF',
                                                                                                    'CALL']:
                                    result.append(parent.children[index].line)
                                    result.append(parent.children[index + 1].line)
                        elif param_first == '_' and parent.children[index].node_type in ['WHILE', 'ASSIGN', 'IF',
                                                                                         'CALL']:
                            if len(parent.children) > index+1:
                                if parent.children[index + 1].node_type == param_second:
                                    result.append(parent.children[index].line)
                                    result.append(parent.children[index + 1].line)
                                if param_second == '_' and parent.children[index + 1].node_type in ['WHILE', 'ASSIGN', 'IF',
                                                                                                    'CALL']:
                                    result.append(parent.children[index].line)
                                    result.append(parent.children[index + 1].line)

                return list(set(result))
                # if p1 i p2 sa w tej samej stmt_lst
                # if p1 i p2 maja odpowiedni rodzaj
                # linia p1+1 = linia p2
                pass

    def followsT(self, param_first: str, param_second: str) -> List[int]:
        if param_first.isdigit():
            if param_second.isdigit():
                pass
                # p1 i p2 sa liczbami
                # if p1 i p2 sa w tej samej stmt_lst
                # if p1 < p2
            else:
                # p1 jest liczba, a p2 nie
                # if p1+1 jest w tej samej stmt_lst and rodzaj p2 sie zgadza(czy jest to while, assign lub if)
                # i linia p2 > p1
                pass
        else:
            if param_second.isdigit():
                pass
                # p1 nie jest liczba, a p2 jest liczba
                # if p2-1 jest w tej samej stmt_lst and rodzaj p1 sie zgadza(czy jest to while, assign lub if)
                # i linia p1 < p2-1
            else:
                # p1 i p2 nie sa liczbami
                # if p1 i p2 sa w tej samej stmt_lst
                # if p1 i p2 maja odpowiedni rodzaj
                # linia p1+1 < linia p2
                pass


if __name__ == '__main__':
    rel: FollowsRelation = FollowsRelation()
