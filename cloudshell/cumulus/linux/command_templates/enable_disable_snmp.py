from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.cumulus.linux.command_templates import ERROR_MAP


SHOW_SNMP_STATUS = CommandTemplate("net show snmp-server status", error_map=ERROR_MAP)

ADD_LISTENING_ADDRESS = CommandTemplate('net add snmp-server listening-address all', error_map=ERROR_MAP)

CREATE_VIEW = CommandTemplate('net add snmp-server viewname {view_name} included .1', error_map=ERROR_MAP)

ENABLE_SNMP_READ = CommandTemplate('net add snmp-server readonly-community {snmp_community} access any '
                                   'view {view_name}', error_map=ERROR_MAP)

ENABLE_SNMP_USER = CommandTemplate('net add snmp-server username {snmp_user} {snmp_auth_proto} {snmp_password} '
                                   '{snmp_priv_proto} {snmp_priv_key} view {view_name}', error_map=ERROR_MAP)

REMOVE_LISTENING_ADDRESS = CommandTemplate('net del snmp-server listening-address all', error_map=ERROR_MAP)

REMOVE_VIEW = CommandTemplate('net del snmp-server viewname {view_name} included .1', error_map=ERROR_MAP)

DISABLE_SNMP_READ = CommandTemplate('net del snmp-server readonly-community {snmp_community}', error_map=ERROR_MAP)

DISABLE_SNMP_USER = CommandTemplate('net del snmp-server username {snmp_user}', error_map=ERROR_MAP)

COMMIT = CommandTemplate('net commit', error_map=ERROR_MAP)

ABORT = CommandTemplate('net abort', error_map=ERROR_MAP)
