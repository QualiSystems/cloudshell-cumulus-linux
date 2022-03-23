from cloudshell.snmp.autoload.generic_snmp_autoload import GenericSNMPAutoload

from cloudshell.cumulus.linux.snmp.snmp_entitiy_table import CumulusSnmpEntityTable
from cloudshell.cumulus.linux.snmp.system_info import CumulusSystemInfo


class CumulusSNMPAutoload(GenericSNMPAutoload):
    @property
    def system_info_service(self) -> CumulusSystemInfo:
        if not self._system_info:
            self._system_info = CumulusSystemInfo(self.snmp_handler, self.logger)
        return self._system_info

    @property
    def entity_table_service(self):
        if not self._entity_table:
            self._entity_table = CumulusSnmpEntityTable(
                snmp_handler=self.snmp_handler,
                logger=self.logger,
                if_table=self.if_table_service,
            )
        return self._entity_table
