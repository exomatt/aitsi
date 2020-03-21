import json

from anytree.exporter import UniqueDotExporter
from anytree.importer import DictImporter

importer = DictImporter()
filename = 'AST.json'
with open(filename) as json_file:
    data = json.load(json_file)


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


new_json = json.loads(json.dumps(data), object_hook=remove_dots)

root = importer.import_(new_json)

out_filename = "tree.png"
UniqueDotExporter(root).to_picture(out_filename)
