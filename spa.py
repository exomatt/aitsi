import sys

import main_parser
import main_pql


def main(argv):
    db_path = main_parser.main(argv[1])
    print("Ready")
    pql = main_pql.PQL(db_path)
    while True:
        first_line = input()
        second_line = input()
        result: str = pql.main(first_line + " " + second_line)
        print(result)


if __name__ == "__main__":
    main(sys.argv)
