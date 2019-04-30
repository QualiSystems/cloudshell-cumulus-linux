from cloudshell.cli.command_mode import CommandMode


class DefaultCommandMode(CommandMode):
    PROMPT = r"\$\s*$"
    ENTER_COMMAND = ''
    EXIT_COMMAND = 'exit'

    def __init__(self, resource_config, api):
        """Initialize Default command mode, only for cases when session started not in enable mode

        :param resource_config:
        """
        self.resource_config = resource_config
        self._api = api

        super(DefaultCommandMode, self).__init__(DefaultCommandMode.PROMPT,
                                                 DefaultCommandMode.ENTER_COMMAND,
                                                 DefaultCommandMode.EXIT_COMMAND)


class RootCommandMode(CommandMode):
    PROMPT = r"#\s*$"
    ENTER_COMMAND = 'sudo -i'
    EXIT_COMMAND = "exit"

    def __init__(self, resource_config, api):
        """
        Initialize Config command mode
        :param resource_config:
        """

        self.resource_config = resource_config
        self._api = api
        self._root_password = None

        CommandMode.__init__(self,
                             RootCommandMode.PROMPT,
                             RootCommandMode.ENTER_COMMAND,
                             RootCommandMode.EXIT_COMMAND,
                             enter_action_map=self.enter_action_map())

    @property
    def root_password(self):
        """

        :return:
        """
        if not self._root_password:
            self._root_password = self._api.DecryptPassword(self.resource_config.enable_password).Value

        return self._root_password

    def enter_action_map(self):
        return {"[Pp]assword": lambda session, logger: session.send_line(self.root_password, logger)}


CommandMode.RELATIONS_DICT = {
    DefaultCommandMode: {
        RootCommandMode: {}
    }
}
