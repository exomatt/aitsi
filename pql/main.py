import sys

from pql.Parser import Parser

if __name__ == '__main__':
    if len(sys.argv) != 1:
        query: str = sys.argv[1]
        parser: Parser = Parser()
        response: str = parser.parse(query)
        print(response)         #fixme decyzja jakie wyjscie:plik, konsola