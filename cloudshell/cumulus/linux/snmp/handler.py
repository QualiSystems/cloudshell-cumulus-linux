from cloudshell.cumulus.linux.flows.disable_snmp import CumulusLinuxDisableSnmpFlow
from cloudshell.cumulus.linux.flows.enable_snmp import CumulusLinuxEnableSnmpFlow
from cloudshell.devices.snmp_handler import SnmpHandler


class CumulusLinuxSnmpHandler(SnmpHandler):
    def __init__(self, resource_config, logger, api, cli_handler):
        """

        :param resource_config:
        :param logger:
        :param api:
        :param cli_handler:
        """
        super(CumulusLinuxSnmpHandler, self).__init__(resource_config, logger, api)
        self.cli_handler = cli_handler

    def _create_enable_flow(self):
        """

        :return:
        """
        return CumulusLinuxEnableSnmpFlow(cli_handler=self.cli_handler, logger=self._logger)

    def _create_disable_flow(self):
        """

        :return:
        """
        return CumulusLinuxDisableSnmpFlow(cli_handler=self.cli_handler, logger=self._logger)
