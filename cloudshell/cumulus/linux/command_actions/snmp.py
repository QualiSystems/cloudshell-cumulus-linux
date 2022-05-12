import re
from logging import Logger

import attr

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.service.cli_service import CliService

from cloudshell.cumulus.linux.command_templates import enable_disable_snmp

SNMP_ACTIVE_PATTERN = re.compile(r"current[\s]+status[\s]+active", flags=re.I | re.M)


@attr.s(auto_attribs=True, slots=True, frozen=True)
class BaseSnmpActions:
    _cli_service: CliService
    _logger: Logger

    def is_snmp_running(self) -> bool:
        snmp_status = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.SHOW_SNMP_STATUS
        ).execute_command()
        return bool(SNMP_ACTIVE_PATTERN.search(snmp_status))
