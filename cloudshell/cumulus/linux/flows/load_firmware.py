from logging import Logger

from cloudshell.shell.flows.firmware.basic_flow import AbstractFirmwareFlow

from cloudshell.cumulus.linux.cli.handler import CumulusCliConfigurator
from cloudshell.cumulus.linux.command_actions.firmware import FirmwareActions
from cloudshell.cumulus.linux.command_actions.system import SystemActions


class LoadFirmwareFlow(AbstractFirmwareFlow):
    def __init__(self, logger: Logger, cli_configurator: CumulusCliConfigurator):
        super().__init__(logger)
        self._cli_configurator = cli_configurator

    def _load_firmware_flow(self, path: str, vrf_management_name: str, timeout) -> str:
        with self._cli_configurator.root_mode_service() as cli_service:
            sys_act = SystemActions(cli_service, self._logger)
            firmware_act = FirmwareActions(cli_service, self._logger)

            self._logger.info(f"Loading firmware: {path}")
            output = firmware_act.load_firmware(path, timeout)

            try:
                self._logger.info("Rebooting device...")
                output += sys_act.reboot()
            except Exception:
                self._logger.debug("Reboot session exception:", exc_info=True)

            self._logger.info("Reconnecting session...")
            cli_service.reconnect(timeout)
            return output
