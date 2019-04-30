from cloudshell.cumulus.linux.autoload.snmp import CumulusLinuxSNMPAutoload
from cloudshell.devices.flows.snmp_action_flows import AutoloadFlow


class CumulusLinuxSnmpAutoloadFlow(AutoloadFlow):
    def execute_flow(self, supported_os, shell_name, shell_type, resource_name):
        """

        :param supported_os:
        :param shell_name:
        :param shell_type:
        :param resource_name:
        :return:
        """
        with self._snmp_handler.get_snmp_service() as snmp_service:
            cisco_snmp_autoload = CumulusLinuxSNMPAutoload(snmp_handler=snmp_service,
                                                           shell_name=shell_name,
                                                           shell_type=shell_type,
                                                           resource_name=resource_name,
                                                           logger=self._logger)

            return cisco_snmp_autoload.discover(supported_os)
