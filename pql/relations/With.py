from typing import Dict, Union, Set

from aitsi_parser.CallsTable import CallsTable
from aitsi_parser.ConstTable import ConstTable
from aitsi_parser.FollowsTable import FollowsTable
from aitsi_parser.ModifiesTable import ModifiesTable
from aitsi_parser.NextTable import NextTable
from aitsi_parser.ParentTable import ParentTable
from aitsi_parser.ProcTable import ProcTable
from aitsi_parser.StatementTable import StatementTable
from aitsi_parser.UsesTable import UsesTable
from aitsi_parser.VarTable import VarTable
from pql.Node import Node


class With:

    def __init__(self, all_tables: Dict[str, Union[VarTable,
                                                   ProcTable,
                                                   UsesTable,
                                                   ParentTable,
                                                   ModifiesTable,
                                                   FollowsTable,
                                                   CallsTable,
                                                   StatementTable,
                                                   ConstTable,
                                                   NextTable]]):
        self.all_tables: Dict[str, Union[VarTable,
                                         ProcTable,
                                         UsesTable,
                                         ParentTable,
                                         ModifiesTable,
                                         FollowsTable,
                                         CallsTable,
                                         StatementTable,
                                         ConstTable,
                                         NextTable]] = all_tables

    def execute(self, attr_node: Node) -> Union[Set[str], Set[int]]:
        if attr_node.children[1].node_type == 'INTEGER':
            if attr_node.children[0].node_type == 'CONSTANT':
                if not self.all_tables['const'].is_in(int(attr_node.children[1].value)):
                    return set()
            elif attr_node.children[0].node_type in ['STMT', 'PROG_LINE']:
                if int(attr_node.children[1].value) > self.all_tables['statement'].get_size():
                    return set()
            else:
                if int(attr_node.children[1].value) not in self.all_tables['statement'].get_statement_line_by_type_name(
                        attr_node.children[0].node_type):
                    return set()
            return {attr_node.children[1].value}
        elif attr_node.children[1].node_type == 'IDENT_QUOTE':
            if attr_node.children[0].node_type == 'PROCEDURE':
                if not self.all_tables['proc'].is_in(attr_node.children[1].value):
                    return set()
            elif attr_node.children[0].node_type == 'VARIABLE':
                if not self.all_tables['var'].is_in(attr_node.children[1].value):
                    return set()
            else:
                return set(self.all_tables['statement'].get_statement_line_by_type_name_and_value(
                    attr_node.children[0].node_type,
                    attr_node.children[1].value))
            return {attr_node.children[1].value}
        elif attr_node.children[1].node_type == 'CONSTANT':
            if attr_node.children[0].node_type == 'STMT':
                return set([const for const in self.all_tables['const'].get_all_constant() if
                            self.all_tables['statement'].is_in(const)])
            else:
                return set([const for const in self.all_tables['const'].get_all_constant() if
                            const in self.all_tables[
                                'statement'].get_statement_line_by_type_name(
                                attr_node.children[0].value)])
        else:
            if attr_node.children[0].node_type in ['CALL', 'PROCEDURE']:
                left: Set[str] = set(self.all_tables['proc'].get_all_proc_name())
            else:
                left: Set[str] = set(self.all_tables['var'].get_all_var_name())

            if attr_node.children[1].node_type in ['CALL', 'PROCEDURE']:
                right: Set[str] = set(self.all_tables['proc'].get_all_proc_name())
            else:
                right: Set[str] = set(self.all_tables['var'].get_all_var_name())

            return left.intersection(right)
