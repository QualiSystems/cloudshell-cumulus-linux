from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cumulus.linux.cli.command_modes import DefaultCommandMode
from cloudshell.cumulus.linux.cli.command_modes import RootCommandMode
from cloudshell.devices.cli_handler_impl import CliHandlerImpl


class CumulusCliHandler(CliHandlerImpl):
    def __init__(self, cli, resource_config, logger, api):
        super(CumulusCliHandler, self).__init__(cli, resource_config, logger, api)
        self.modes = CommandModeHelper.create_command_mode(resource_config, api)

    @property
    def enable_mode(self):
        return self.modes[DefaultCommandMode]

    @property
    def config_mode(self):
        return self.modes[DefaultCommandMode]

    @property
    def root_mode(self):
        return self.modes[RootCommandMode]

