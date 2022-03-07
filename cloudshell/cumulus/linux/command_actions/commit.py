from logging import Logger
from typing import ClassVar

import attr

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.service.cli_service import CliService

from cloudshell.cumulus.linux.command_templates import commit_abort


@attr.s(auto_attribs=True, slots=True, frozen=True)
class CommitActions:
    COMMIT_COMMAND_TIMEOUT: ClassVar[int] = 5 * 60
    ABORT_COMMAND_TIMEOUT: ClassVar[int] = 5 * 60
    _cli_service: CliService
    _logger: Logger

    def commit(self) -> str:
        return CommandTemplateExecutor(
            self._cli_service, commit_abort.COMMIT, timeout=self.COMMIT_COMMAND_TIMEOUT
        ).execute_command()

    def abort(self) -> str:
        return CommandTemplateExecutor(
            self._cli_service, commit_abort.ABORT, timeout=self.ABORT_COMMAND_TIMEOUT
        ).execute_command()
