from __future__ import annotations

from logging import Logger

import attr

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.service.cli_service import CliService

from cloudshell.cumulus.linux.command_templates import state


@attr.s(auto_attribs=True, slots=True, frozen=True)
class StateActions:
    _cli_service: CliService
    _logger: Logger

    def shutdown(
        self, action_map: dict | None = None, error_map: dict | None = None
    ) -> str:
        return CommandTemplateExecutor(
            self._cli_service,
            state.SHUTDOWN,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()
