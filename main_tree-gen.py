import json
import argparse
from anytree.exporter import UniqueDotExporter
from anytree.importer import DictImporter

importer = DictImporter()

def remove_dots(obj):
    for key in obj.keys():
        new_key = key.replace("node_type", "name")
        if new_key != key:
            if obj['value'].strip() in ['{', '}', '']:
                obj[new_key] = "Node_type: " + obj[key] + "\n" + "Line: " + str(
                    obj['line'])
            else:
                obj[new_key] = "Node_type: " + obj[key] + "\n" + "Value: " + obj['value'] + "\n" + "Line: " + str(
                    obj['line'])
            del obj[key]
    return obj

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Tree Gnerator!')
    arg_parser.add_argument("--i", default="AST.json", type=str, help="Input JSON file with Nodes")
    arg_parser.add_argument("--o", default="tree.png", type=str, help="Output image for tree ")
    args: argparse.Namespace = arg_parser.parse_args()
    input_filename: str = args.i
    output_filename: str = args.o

    with open(input_filename) as json_file:
        data = json.load(json_file)

    new_json = json.loads(json.dumps(data), object_hook=remove_dots)

    root = importer.import_(new_json)

    UniqueDotExporter(root).to_picture(output_filename)