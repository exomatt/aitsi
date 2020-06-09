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
            return {int(attr_node.children[1].value)}
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
        else:
            if attr_node.children[0].node_type == 'STMT':
                if attr_node.children[1].node_type == 'STMT':
                    return set(self.all_tables['statement'].get_all_statement_lines())
                elif attr_node.children[1].node_type == 'CONSTANT':
                    return set(self.all_tables['const'].get_all_constant()).intersection(
                        self.all_tables['statement'].get_all_statement_lines())
                return set(
                    self.all_tables['statement'].get_statement_line_by_type_name(attr_node.children[1].node_type))
            elif attr_node.children[0].node_type == 'PROCEDURE':
                if attr_node.children[1].node_type == 'PROCEDURE':
                    return set(self.all_tables['proc'].get_all_proc_name())
                elif attr_node.children[1].node_type == 'CALL':
                    return set(self.all_tables['calls'].table.columns.tolist())
                return set(self.all_tables['var'].get_all_var_name()).intersection(
                    self.all_tables['proc'].get_all_proc_name())
            elif attr_node.children[0].node_type == 'CALL':
                if attr_node.children[0].children[0].value == 'stmt#':
                    if attr_node.children[1].node_type in ['STMT', 'CALL']:
                        return set(self.all_tables['statement'].get_statement_line_by_type_name('CALL'))
                    return set(self.all_tables['statement'].get_statement_line_by_type_name(
                        attr_node.children[1].node_type)).intersection(
                        self.all_tables['statement'].get_statement_line_by_type_name('CALL'))
                if attr_node.children[1].node_type == 'PROCEDURE':
                    return set(self.all_tables['calls'].table.columns.tolist())
                elif attr_node.children[1].node_type == 'VARIABLE':
                    return set(self.all_tables['var'].get_all_var_name()).intersection(
                        self.all_tables['proc'].get_all_proc_name())
            elif attr_node.children[0].node_type == 'CONSTANT':
                if attr_node.children[1].node_type == 'STMT':
                    return set(self.all_tables['statement'].get_all_statement_lines()).intersection(
                        self.all_tables['const'].get_all_constant())
                elif attr_node.children[1].node_type == 'CONSTANT':
                    return set(self.all_tables['const'].get_all_constant())
                return set(self.all_tables['statement'].get_statement_line_by_type_name(
                    attr_node.children[1].node_type)).intersection(self.all_tables['const'].get_all_constant())
            elif attr_node.children[0].node_type == 'VARIABLE':
                if attr_node.children[1].node_type == 'PROCEDURE':
                    return set(self.all_tables['proc'].get_all_proc_name()).intersection(
                        self.all_tables['var'].get_all_var_name())
                return set(self.all_tables['var'].get_all_var_name())
            if attr_node.children[1].node_type == 'STMT':
                return set(
                    self.all_tables['statement'].get_statement_line_by_type_name(attr_node.children[0].node_type))
            elif attr_node.children[1].node_type == 'CONSTANT':
                return set(self.all_tables['const'].get_all_constant()).intersection(
                    self.all_tables['statement'].get_statement_line_by_type_name(attr_node.children[0].node_type))
            return set(self.all_tables['statement'].get_statement_line_by_type_name(
                attr_node.children[1].node_type)).intersection(
                self.all_tables['statement'].get_statement_line_by_type_name(attr_node.children[0].node_type))
