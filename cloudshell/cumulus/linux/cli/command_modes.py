from cloudshell.cli.service.command_mode import CommandMode
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
        self._root_password = None

        super().__init__(
            self.PROMPT,
            self.ENTER_COMMAND,
            self.EXIT_COMMAND,
            enter_action_map=self.enter_action_map(),
        )

    @property
    def root_password(self):
        if not self._root_password:
            self._root_password = self._api.DecryptPassword(
                self.resource_config.enable_password
            ).Value

        return self._root_password

    def enter_action_map(self) -> dict:
        return {
            r"[Pp]assword": lambda session, logger: session.send_line(
                self.root_password, logger
            )
        }


CommandMode.RELATIONS_DICT = {
    DefaultCommandMode: {
        RootCommandMode: {},
    },
}
