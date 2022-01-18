from logging import Logger

from cloudshell.cli.configurator import AbstractModeConfigurator
from cloudshell.cli.service.cli import CLI
from cloudshell.cli.service.command_mode_helper import CommandModeHelper
from cloudshell.cli.service.session_pool_manager import SessionPoolManager
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.shell.standards.networking.resource_config import (
    NetworkingResourceConfig,
)

from cloudshell.cumulus.linux.cli.command_modes import (
    DefaultCommandMode,
    RootCommandMode,
)


def get_cli(resource_config: NetworkingResourceConfig) -> CLI:
    session_pool_size = int(resource_config.sessions_concurrency_limit)
    session_pool = SessionPoolManager(max_pool_size=session_pool_size)
    return CLI(session_pool=session_pool)


class CumulusCliHandler(AbstractModeConfigurator):
    REGISTERED_SESSIONS = (SSHSession, TelnetSession)

    def __init__(
        self, cli: CLI, resource_config: NetworkingResourceConfig, logger: Logger
    ):
        super().__init__(resource_config, logger, cli)
        self.modes = CommandModeHelper.create_command_mode(resource_config)

    @property
    def enable_mode(self) -> DefaultCommandMode:
        return self.modes[DefaultCommandMode]

    @property
    def config_mode(self) -> DefaultCommandMode:
        return self.modes[DefaultCommandMode]

    @property
    def root_mode(self) -> RootCommandMode:
        return self.modes[RootCommandMode]
