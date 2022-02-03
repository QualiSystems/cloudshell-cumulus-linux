from __future__ import annotations

from logging import Logger

from cloudshell.shell.core.driver_context import AutoLoadDetails
from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow
from cloudshell.shell.standards.networking.autoload_model import NetworkingResourceModel
from cloudshell.snmp.autoload.generic_snmp_autoload import GenericSNMPAutoload

from cloudshell.cumulus.linux.snmp.handler import CumulusEnableDisableSnmpConfigurator


class AutoloadFlow(AbstractAutoloadFlow):
    def __init__(
        self, logger: Logger, snmp_configurator: CumulusEnableDisableSnmpConfigurator
    ):
        super().__init__(logger)
        self._snmp_configurator = snmp_configurator

    def _autoload_flow(
        self, supported_os: list[str], resource_model: NetworkingResourceModel
    ) -> AutoLoadDetails:
        with self._snmp_configurator.get_service() as snmp_service:
            autoload_handler = GenericSNMPAutoload(snmp_service, self._logger)
            return autoload_handler.discover(supported_os, resource_model)
