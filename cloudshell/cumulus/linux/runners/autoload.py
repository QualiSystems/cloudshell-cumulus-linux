from cloudshell.cumulus.linux.flows.autoload import CumulusLinuxSnmpAutoloadFlow
from cloudshell.devices.runners.autoload_runner import AutoloadRunner


class CumulusLinuxAutoloadRunner(AutoloadRunner):
    def __init__(self, logger, resource_config, snmp_handler):
        """

        :param logger:
        :param resource_config:
        :param snmp_handler:
        """
        super(CumulusLinuxAutoloadRunner, self).__init__(resource_config=resource_config, logger=logger)
        self.snmp_handler = snmp_handler

    @property
    def autoload_flow(self):
        """

        :return:
        """
        return CumulusLinuxSnmpAutoloadFlow(snmp_handler=self.snmp_handler,
                                            logger=self._logger)
