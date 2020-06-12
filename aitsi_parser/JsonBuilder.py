import json
from typing import Union, Dict, List


class JsonBuilder:

    @staticmethod
    def save_table_to_json_file(data_table: Union[Dict, List], path: str):
        with open(path, 'w+') as f:
            json.dump(data_table, f)
