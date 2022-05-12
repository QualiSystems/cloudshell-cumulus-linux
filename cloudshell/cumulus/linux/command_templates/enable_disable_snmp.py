from cloudshell.cli.command_template.command_template import CommandTemplate

from cloudshell.cumulus.linux.command_templates import ERROR_MAP

SHOW_SNMP_STATUS = CommandTemplate("net show snmp-server status", error_map=ERROR_MAP)
