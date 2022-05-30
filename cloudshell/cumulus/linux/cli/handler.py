from __future__ import annotations

from logging import Logger
from typing import TYPE_CHECKING

from cloudshell.cli.configurator import AbstractModeConfigurator
from cloudshell.cli.service.cli import CLI
from cloudshell.cli.service.command_mode_helper import CommandModeHelper
from cloudshell.cli.service.session_pool_context_manager import (
    SessionPoolContextManager,
)
from cloudshell.cli.service.session_pool_manager import SessionPoolManager

from cloudshell.cumulus.linux.cli.command_modes import (
    DefaultCommandMode,
    RootCommandMode,
)

if TYPE_CHECKING:
    from cloudshell.shell.standards.networking.resource_config import (
        NetworkingResourceConfig,
    )


def get_cli(resource_config: NetworkingResourceConfig) -> CLI:
    session_pool_size = int(resource_config.sessions_concurrency_limit)
    session_pool = SessionPoolManager(max_pool_size=session_pool_size)
    return CLI(session_pool=session_pool)


class CumulusCliConfigurator(AbstractModeConfigurator):
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

    def root_mode_service(self) -> SessionPoolContextManager:
        return self.get_cli_service(self.root_mode)
