from typing import List, Optional, Union

from pql.Node import Node
from pql.utils.SearchUtils import SearchUtils


class FollowsRelation:
    def __init__(self, ast_tree: Node) -> None:
        super().__init__()
        self.ast_tree: Node = ast_tree

    def follows(self, param_first: str, param_second: str) -> List[int]:
        search_utils: SearchUtils = SearchUtils(self.ast_tree)
        if param_first.isdigit():
            if param_second.isdigit():
                pass
                # p1 i p2 sa liczbami
                p1_node: Optional[Node] = search_utils.find_node_by_line(int(param_first))
                p2_node: Optional[Node] = search_utils.find_node_by_line(int(param_second))
                if p1_node is None or p2_node is None:
                    return False
                else:

                    stmt_list: List[Node] = []
                # if p1 i p2 sa w tej samej stmt_lst
                # if p1+1 = p2
            else:
                # p1 jest liczba, a p2 nie
                # if p1+1 jest w tej samej stmt_lst and rodzaj p2 sie zgadza(czy jest to while, assign lub if)
                # i linia p2-1 = p1
                pass
        else:
            if param_second.isdigit():
                pass
                # p1 nie jest liczba, a p2 jest liczba
                # if p2-1 jest w tej samej stmt_lst and rodzaj p1 sie zgadza(czy jest to while, assign lub if)
                # i linia p1 = p2-1
            else:
                # p1 i p2 nie sa liczbami
                # if p1 i p2 sa w tej samej stmt_lst
                # if p1 i p2 maja odpowiedni rodzaj
                # linia p1+1 = linia p2
                pass

    def follows_t(self, param_first: str, param_second: str) -> List[int]:
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
