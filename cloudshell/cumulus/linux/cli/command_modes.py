from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.cli.service.command_mode import CommandMode

if TYPE_CHECKING:
    from cloudshell.shell.standards.networking.resource_config import (
        NetworkingResourceConfig,
    )


class DefaultCommandMode(CommandMode):
    PROMPT = r"\$\s*$"
    ENTER_COMMAND = ""
    EXIT_COMMAND = "exit"

    def __init__(self, resource_config: NetworkingResourceConfig):
        self.resource_config = resource_config
        super().__init__(self.PROMPT, self.ENTER_COMMAND, self.EXIT_COMMAND)


class RootCommandMode(CommandMode):
    PROMPT = r"#\s*$"
    ENTER_COMMAND = "sudo -i"
    EXIT_COMMAND = "exit"

    def __init__(self, resource_config: NetworkingResourceConfig):
        self.resource_config = resource_config

        super().__init__(
            self.PROMPT,
            self.ENTER_COMMAND,
            self.EXIT_COMMAND,
            enter_action_map=self.enter_action_map(),
        )

    def enter_action_map(self) -> dict:
        return {
            r"[Pp]assword": lambda session, logger: session.send_line(
                self.resource_config.enable_password, logger
            )
        }


CommandMode.RELATIONS_DICT = {
    DefaultCommandMode: {
        RootCommandMode: {},
    },
}
