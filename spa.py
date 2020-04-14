import logging
import sys
from typing import Union, List

import main_parser
import main_pql

log = logging.getLogger(__name__)


def main(argv):
    db_path = main_parser.main(argv[1])
    print("Ready")
    while True:
        first_line = input()
        second_line = input()
        result: Union[bool, List[str], List[int]] = main_pql.main(first_line + " " + second_line, db_path)
        print(result)


if __name__ == "__main__":
    log_format = "%(asctime)s::%(levelname)s::%(name)s::" \
                 "%(filename)s::%(lineno)d::%(message)s"
    logging.basicConfig(filename='spa.log', level=logging.DEBUG, format=log_format)
    main(sys.argv)
