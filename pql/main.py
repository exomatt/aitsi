import sys

from pql.Parser import Parser

if __name__ == '__main__':
    if len(sys.argv) != 1:
        query: str = sys.argv[1]
        parser: Parser = Parser()
        parser.parse(query)
        # fixme decyzja jakie wyjscie:plik, konsola
