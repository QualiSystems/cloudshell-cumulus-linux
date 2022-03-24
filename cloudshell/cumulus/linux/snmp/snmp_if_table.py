from cloudshell.snmp.autoload.snmp_if_table import SnmpIfTable


class CumulusSnmpIfTable(SnmpIfTable):
    PORT_EXCLUDE_LIST = [*SnmpIfTable.PORT_EXCLUDE_LIST, "br_", "vni-"]
