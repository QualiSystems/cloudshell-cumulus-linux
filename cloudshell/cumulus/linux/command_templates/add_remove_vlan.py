from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.cumulus.linux.command_templates import ERROR_MAP


ADD_PORT_TO_BRIDGE = CommandTemplate("net add bridge bridge ports {port}", error_map=ERROR_MAP)

ALLOW_TRUNK_VLAN_ON_PORT = CommandTemplate("net add interface {port} bridge vids {vlan_range}", error_map=ERROR_MAP)

ADD_ACCESS_VLAN_TO_PORT = CommandTemplate("net add interface {port} bridge access {vlan}", error_map=ERROR_MAP)

REMOVE_PORT_FROM_BRIDGE = CommandTemplate("net del bridge bridge ports {port}", error_map=ERROR_MAP)

REMOVE_TRUNK_VLAN_ON_PORT = CommandTemplate("net del interface {port} bridge vids", error_map=ERROR_MAP)

REMOVE_ACCESS_VLAN_ON_PORT = CommandTemplate("net del interface {port} bridge access", error_map=ERROR_MAP)
