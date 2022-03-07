from cloudshell.snmp.autoload.generic_snmp_autoload import GenericSNMPAutoload

from cloudshell.cumulus.linux.snmp.system_info import CumulusSystemInfo


class CumulusSNMPAutoload(GenericSNMPAutoload):
    @property
    def system_info_service(self) -> CumulusSystemInfo:
        if not self._system_info:
            self._system_info = CumulusSystemInfo(self.snmp_handler, self.logger)
        return self._system_info
