import re

from cloudshell.snmp.autoload.constants.port_constants import PORT_NAME
from cloudshell.snmp.autoload.snmp_if_table import SnmpIfTable


class CumulusSnmpIfTable(SnmpIfTable):
    PORT_NAME_EXCLUDE_PATTERN = re.compile(r"^(br_\S+|vni-\d+|^eth\d+)$")

    def _add_port(self, port):
        name = self._snmp.get_property(
            PORT_NAME.get_snmp_mib_oid(port.index)
        ).safe_value
        if not self.PORT_NAME_EXCLUDE_PATTERN.search(name):
            super()._add_port(port)
