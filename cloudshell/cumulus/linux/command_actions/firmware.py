from logging import Logger

import attr

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.service.cli_service import CliService

from cloudshell.cumulus.linux.command_templates import firmware


@attr.s(auto_attribs=True, slots=True, frozen=True)
class FirmwareActions:
    _cli_service: CliService
    _logger: Logger

    def load_firmware(self, image_path: str, timeout) -> str:
        return CommandTemplateExecutor(
            self._cli_service, firmware.LOAD_FIRMWARE, timeout=timeout
        ).execute_command(image_path=image_path)
