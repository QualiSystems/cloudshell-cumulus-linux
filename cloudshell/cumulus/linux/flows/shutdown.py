from cloudshell.shell.flows.state.basic_flow import StateFlow

from cloudshell.cumulus.linux.cli.handler import CumulusCliConfigurator
from cloudshell.cumulus.linux.command_actions.system import SystemActions


class CumulusLinuxShutdownFlow(StateFlow):
    _cli_configurator: CumulusCliConfigurator

    def shutdown(self):
        with self._cli_configurator.root_mode_service() as cli_service:
            return SystemActions(cli_service, self._logger).shutdown()
