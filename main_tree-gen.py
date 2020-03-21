from anytree.importer import DictImporter
from anytree import RenderTree
from anytree.exporter import UniqueDotExporter
import json
importer = DictImporter()
with open('AST.json') as json_file:
    data = json.load(json_file)

def remove_dots(obj):
    for key in obj.keys():
        new_key = key.replace("node_type","name")
        if new_key != key:
            obj[new_key] = obj[key]
            del obj[key]
    return obj

new_json = json.loads(json.dumps(data), object_hook=remove_dots) 

root = importer.import_(new_json)

UniqueDotExporter(root).to_picture("tree.png")