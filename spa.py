import sys
from typing import Union, List

import main_parser
import main_pql


def main(argv):
    db_path = main_parser.main(argv[1])
    print("Ready")
    while True:
        first_line = input()
        second_line = input()
        result: Union[bool, List[str], List[int]] = main_pql.main(first_line + " " + second_line, db_path)
        print(result)


if __name__ == "__main__":
    main(sys.argv)
