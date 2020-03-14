from Parser import Parser

if __name__ == '__main__':
    with open('code_short.txt') as f:
        parser: Parser = Parser(f.read())
    parser.program()
    parser.root.to_string(1)
