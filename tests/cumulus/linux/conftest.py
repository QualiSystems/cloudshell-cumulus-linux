from __future__ import annotations

from collections import deque
from enum import Enum
from logging import Logger
from typing import Sequence
from unittest.mock import Mock

import attr
import pytest

from cloudshell.cli.configurator import AbstractModeConfigurator
from cloudshell.cli.service.session_manager_impl import SessionManagerImpl
from cloudshell.cli.session.expect_session import ExpectSession
from cloudshell.shell.standards import attribute_names
from cloudshell.shell.standards.networking.resource_config import (
    NetworkingResourceConfig,
)

from cloudshell.cumulus.linux.cli.handler import CumulusCliConfigurator, get_cli


@pytest.fixture()
def logger():
    return Mock()


@pytest.fixture()
def cs_api():
    return Mock(DecryptPassword=lambda pwd: Mock(Value=pwd))


class Prompt(Enum):
    DEFAULT = "cumulus@cumulus:~$ "
    ROOT = "root@cumulus:~# "
    EMPTY = ""


@attr.s(auto_attribs=True, slots=True, frozen=True, str=False)
class Input:
    command: str
    new_line: str = "\r"

    def __str__(self):
        return f"{self.command}{self.new_line}"


@attr.s(auto_attribs=True, slots=True, frozen=True, str=False)
class Output:
    response: str
    prompt: Enum | str = ""

    def __str__(self):
        prompt = self.prompt.value if isinstance(self.prompt, Enum) else self.prompt
        return f"{self.response}\r\n{prompt}"


ENTER_ROOT_MODE = [
    Input("sudo -i"),
    Output("sudo -i\r\n[sudo] password for cumulus: ", Prompt.EMPTY),
    Input("password"),
    Output("", Prompt.ROOT),
]


@pytest.fixture()
def resource_conf(cs_api):
    shell_name = "shell_name"
    attrs = {
        f"{attribute_names.VRF_MANAGEMENT_NAME}": "mgmt-vrf",
        f"{attribute_names.USER}": "user",
        f"{attribute_names.PASSWORD}": "password",
        f"{attribute_names.ENABLE_PASSWORD}": "password",
        f"{attribute_names.SESSION_CONCURRENCY_LIMIT}": 1,
        f"{attribute_names.CLI_CONNECTION_TYPE}": "Auto",
    }
    attrs = {f"{shell_name}.{key}": val for key, val in attrs.items()}
    return NetworkingResourceConfig(shell_name, attributes=attrs, api=cs_api)


@pytest.fixture()
def cli_emu(resource_conf, logger):
    return CliEmu(
        logger,
        resource_conf,
        cli_configurator_cls=CumulusCliConfigurator,
    )


class CliEmu:
    def __init__(
        self,
        logger: Logger,
        resource_conf: NetworkingResourceConfig,
        cli_configurator_cls: type[AbstractModeConfigurator] = AbstractModeConfigurator,
    ):
        self.logger = logger
        self.resource_conf = resource_conf
        self.cli_configurator_cls = cli_configurator_cls
        self.expected_ios = deque()

    def create_cli(emu, expected_ios: Sequence[Input | Output]):
        assert not emu.expected_ios
        expected_ios = deque(expected_ios)
        # probe for prompt
        expected_ios.extendleft((Output("", Prompt.DEFAULT), Input("")))
        emu.expected_ios = expected_ios

        class TestSession(ExpectSession):
            def __init__(self, *args, **kwargs):
                super().__init__()

            def _connect_actions(self, prompt, logger):
                pass

            def _initialize_session(self, prompt, logger):
                pass

            def _set_timeout(self, timeout):
                pass

            def _read_byte_data(self):
                pass

            def disconnect(self):
                self.set_active(False)

            def _clear_buffer(self, timeout, logger):
                return ""

            def _receive_all(self, timeout, logger):
                assert expected_ios
                output = expected_ios.popleft()
                assert isinstance(output, Output)
                return str(output)

            def _send(self, command: str, logger):
                assert expected_ios
                input_ = expected_ios.popleft()
                assert isinstance(input_, Input)
                assert str(input_) == command

        class Cli(emu.cli_configurator_cls):
            REGISTERED_SESSIONS = (TestSession,)

        cli_ = get_cli(emu.resource_conf)
        session_manager = SessionManagerImpl()
        cli_._session_pool._session_manager = session_manager
        return Cli(resource_config=emu.resource_conf, logger=emu.logger, cli=cli_)

    def validate_all_ios_executed(self):
        assert not self.expected_ios
