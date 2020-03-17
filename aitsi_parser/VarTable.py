from typing import List, Dict

import dataclasses
from dataclasses import dataclass
from marshmallow.schema import BaseSchema
from marshmallow_dataclass import add_schema


@dataclass
@add_schema(base_schema=BaseSchema)
class VarTable:
    table: Dict[str, List[str]] = dataclasses.field(default_factory=lambda: {})

    def __init__(self, table: Dict = None) -> None:
        if table is None:
            table = {}
        self.table: Dict[str, List[str]] = table

    def insert_var(self, var_name: str) -> int:
        self.table[var_name] = []
        return list(self.table.keys()).index(var_name)

    def get_var_name(self, index: int) -> str:
        return list(self.table.keys())[index]

    def get_var_index(self, var_name: str) -> int:
        return list(self.table.keys()).index(var_name)

    def get_size(self) -> int:
        return len(self.table)

    def is_in(self, var_name: str) -> bool:
        return var_name in self.table.keys()

    def to_string(self) -> None:
        print("VarTable:")
        for key, value in self.table.items():
            print("Index: " + str(self.get_var_index(key)) + ";\tVar_name: " + key + ";\tOther_info: " + str(value))