from __future__ import annotations

from logging import Logger

from cloudshell.shell.standards.networking.resource_config import (
    NetworkingResourceConfig,
)
from cloudshell.snmp.snmp_configurator import EnableDisableSnmpConfigurator

from cloudshell.cumulus.linux.cli.handler import CumulusCliConfigurator
from cloudshell.cumulus.linux.flows.enable_disable_flow import (
    EnableDisableFlowWithConfig,
)


class CumulusEnableDisableSnmpConfigurator(EnableDisableSnmpConfigurator):
    def __init__(
        self,
        resource_config: NetworkingResourceConfig,
        logger: Logger,
        cli_configurator: CumulusCliConfigurator,
    ):
        # todo use old enable/disable flow for old versions?
        flow = EnableDisableFlowWithConfig(cli_configurator, resource_config, logger)
        super().__init__(flow, resource_config, logger)
