import argparse
import main_parser
import main_pql
import sys

def main(argv):
    print(argv[1])
    main_parser.main(argv[1])

while True:
    sys.stdout.write("Ready")
    main_pql.main()

if __name__ == "__main__": 
    main(sys.argv)