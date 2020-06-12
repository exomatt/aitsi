import json
from typing import List, Dict, Union


class JsonReader:

    @staticmethod
    def read_json_from_file(path: str) -> Union[Dict, List]:
        with open(path, 'r') as f:
            return json.load(f)
