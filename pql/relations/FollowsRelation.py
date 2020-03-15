from typing import List


class FollowsRelation:
    def __init__(self) -> None:
        pass

    def follows(self, param_first: str, param_second: str) -> List[int]:
        if param_first.isdigit():
            if param_second.isdigit():
                pass
                # p1 i p2 sa liczbami
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
