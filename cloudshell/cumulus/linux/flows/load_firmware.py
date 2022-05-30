from __future__ import annotations

from logging import Logger
from typing import TYPE_CHECKING

from cloudshell.shell.flows.firmware.basic_flow import AbstractFirmwareFlow
from cloudshell.shell.flows.utils.url import LocalFileURL

from cloudshell.cumulus.linux.cli.handler import CumulusCliConfigurator
from cloudshell.cumulus.linux.command_actions.firmware import FirmwareActions
from cloudshell.cumulus.linux.command_actions.system import SystemActions

if TYPE_CHECKING:
    from cloudshell.shell.standards.networking.resource_config import (
        NetworkingResourceConfig,
    )


class LoadFirmwareFlow(AbstractFirmwareFlow):
    LOCAL_URL_CLASS = LocalFileURL

    def __init__(
        self,
        logger: Logger,
        resource_config: NetworkingResourceConfig,
        cli_configurator: CumulusCliConfigurator,
    ):
        super().__init__(logger, resource_config)
        self._cli_configurator = cli_configurator

    def _load_firmware_flow(
        self,
        firmware_url: LoadFirmwareFlow.REMOTE_URL_CLASS | LOCAL_URL_CLASS,
        vrf_management_name: str | None,
        timeout: int,
    ) -> None:
        with self._cli_configurator.root_mode_service() as cli_service:
            sys_act = SystemActions(cli_service, self._logger)
            firmware_act = FirmwareActions(cli_service, self._logger)

            self._logger.info(f"Loading firmware: {firmware_url}")
            firmware_act.load_firmware(str(firmware_url), timeout)

            try:
                self._logger.info("Rebooting device...")
                sys_act.reboot()
            except Exception:
                self._logger.debug("Reboot session exception:", exc_info=True)

            self._logger.info("Reconnecting session...")
            cli_service.reconnect(timeout)
