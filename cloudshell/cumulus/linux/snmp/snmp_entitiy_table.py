from cloudshell.snmp.autoload.snmp_entity_table import SnmpEntityTable

from cloudshell.cumulus.linux.snmp.port_mapper import CumulusPortMappingService


class CumulusSnmpEntityTable(SnmpEntityTable):
    @property
    def port_mapping_service(self):
        if not self._port_mapping_service:
            self._port_mapping_service = CumulusPortMappingService(
                self._snmp, self._if_table_service, self._logger
            )
        return self._port_mapping_service
