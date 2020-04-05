from typing import List


class Expressions:

    def __init__(self, code: str) -> None:
        self.code: str = code
        self.split_code: List[str] = []

    def evaluate(self):
        split_after_bracket = [x.split(')') for x in self.code.split('(')[1:]]
        print(self.split_code)