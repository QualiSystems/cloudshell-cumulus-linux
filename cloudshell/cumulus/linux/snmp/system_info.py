from cloudshell.snmp.autoload.snmp_system_info import SnmpSystemInfo


class CumulusSystemInfo(SnmpSystemInfo):
    def _get_vendor(self) -> str:
        return "Cumulus"  # in the SNMP response we have "enterprises"

    def _get_device_model(self) -> str:
        # in the SNMP response we have "enterprises.40310"
        # and we don't have Cumulus Products name MIB
        return ""
