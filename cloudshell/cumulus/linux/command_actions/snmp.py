import re
from logging import Logger

import attr

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.service.cli_service import CliService
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters

from cloudshell.cumulus.linux.command_templates import enable_disable_snmp
from cloudshell.cumulus.linux.const import DEFAULT_VIEW_NAME

SNMP_ACTIVE_PATTERN = re.compile(r"current[\s]+status[\s]+active", flags=re.I | re.M)


@attr.s(auto_attribs=True, slots=True, frozen=True)
class BaseSnmpActions:
    _cli_service: CliService
    _logger: Logger

    def add_listening_address(self) -> str:
        return CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.ADD_LISTENING_ADDRESS
        ).execute_command()

    def add_listening_address_with_vrf(
        self, vrf_management_name: str, ip_address: str
    ) -> str:
        return CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.ADD_LISTENING_ADDRESS_WITH_VRF
        ).execute_command(vrf_name=vrf_management_name, ip_address=ip_address)

    def create_view(self, view_name: str = DEFAULT_VIEW_NAME) -> str:
        return CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.CREATE_VIEW
        ).execute_command(view_name=view_name)

    def remove_listening_address(self) -> str:
        return CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.REMOVE_LISTENING_ADDRESS
        ).execute_command()

    def remove_listening_address_with_vrf(
        self, vrf_management_name: str, ip_address: str
    ) -> str:
        return CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.REMOVE_LISTENING_ADDRESS_WITH_VRF
        ).execute_command(vrf_name=vrf_management_name, ip_address=ip_address)

    def remove_view(self, view_name: str = DEFAULT_VIEW_NAME) -> str:
        return CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.REMOVE_VIEW
        ).execute_command(view_name=view_name)

    def is_snmp_running(self) -> bool:
        snmp_status = CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.SHOW_SNMP_STATUS
        ).execute_command()
        return bool(SNMP_ACTIVE_PATTERN.search(snmp_status))


class SnmpV2Actions(BaseSnmpActions):
    def enable_snmp(
        self,
        snmp_community: str,
        view_name: str = DEFAULT_VIEW_NAME,
    ) -> str:
        return CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.ENABLE_SNMP_READ
        ).execute_command(snmp_community=snmp_community, view_name=view_name)

    def disable_snmp(self, snmp_community: str) -> str:
        return CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.DISABLE_SNMP_READ
        ).execute_command(snmp_community=snmp_community)


class SnmpV3Actions(BaseSnmpActions):
    AUTH_COMMAND_MAP = {
        SNMPV3Parameters.AUTH_NO_AUTH: "auth-none",
        SNMPV3Parameters.AUTH_MD5: "auth-md5",
        SNMPV3Parameters.AUTH_SHA: "auth-sha",
    }

    PRIV_COMMAND_MAP = {
        SNMPV3Parameters.PRIV_NO_PRIV: "",
        SNMPV3Parameters.PRIV_DES: "encrypt-des",
        SNMPV3Parameters.PRIV_AES128: "encrypt-aes",
        # SNMPV3Parameters.PRIV_3DES: "",  not supported by device
        # SNMPV3Parameters.PRIV_AES192: "encrypt-aes",  not supported by device
        # SNMPV3Parameters.PRIV_AES256: "encrypt-aes"   not supported by device
    }

    def enable_snmp(
        self,
        snmp_user: str,
        snmp_password: str,
        snmp_priv_key: str,
        snmp_auth_proto: str,
        snmp_priv_proto: str,
        view_name: str = DEFAULT_VIEW_NAME,
    ) -> str:
        try:
            auth_command_template = self.AUTH_COMMAND_MAP[snmp_auth_proto]
        except KeyError:
            msg = f"Authentication protocol {snmp_auth_proto} is not supported"
            raise Exception(msg)

        try:
            priv_command_template = self.PRIV_COMMAND_MAP[snmp_priv_proto]
        except KeyError:
            raise Exception(f"Privacy Protocol {snmp_priv_proto} is not supported")

        return CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.ENABLE_SNMP_USER
        ).execute_command(
            snmp_user=snmp_user,
            snmp_auth_proto=auth_command_template,
            snmp_password=snmp_password,
            snmp_priv_proto=priv_command_template,
            snmp_priv_key=snmp_priv_key,
            view_name=view_name,
        )

    def disable_snmp(self, snmp_user: str) -> str:
        return CommandTemplateExecutor(
            self._cli_service, enable_disable_snmp.DISABLE_SNMP_USER
        ).execute_command(snmp_user=snmp_user)
