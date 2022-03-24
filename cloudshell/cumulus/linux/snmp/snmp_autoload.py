from cloudshell.snmp.autoload.generic_snmp_autoload import GenericSNMPAutoload

from cloudshell.cumulus.linux.snmp.snmp_if_table import CumulusSnmpIfTable
from cloudshell.cumulus.linux.snmp.system_info import CumulusSystemInfo


class CumulusSNMPAutoload(GenericSNMPAutoload):
    @property
    def system_info_service(self) -> CumulusSystemInfo:
        if not self._system_info:
            self._system_info = CumulusSystemInfo(self.snmp_handler, self.logger)
        return self._system_info

    @property
    def if_table_service(self):
        if not self._if_table:
            self._if_table = CumulusSnmpIfTable(
                snmp_handler=self.snmp_handler, logger=self.logger
            )

        return self._if_table
