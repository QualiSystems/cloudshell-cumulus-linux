from __future__ import annotations

import time
from datetime import datetime, timedelta
from logging import Logger
from typing import ClassVar, Union

import attr

from cloudshell.cli.service.cli_service import CliService
from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.shell.standards.networking.resource_config import (
    NetworkingResourceConfig,
)
from cloudshell.snmp.snmp_configurator import EnableDisableSnmpFlowInterface
from cloudshell.snmp.snmp_parameters import (
    SNMPReadParameters,
    SNMPV3Parameters,
    SNMPWriteParameters,
)

from cloudshell.cumulus.linux import BaseCumulusError
from cloudshell.cumulus.linux.cli.handler import CumulusCliConfigurator
from cloudshell.cumulus.linux.command_actions.commit import CommitActions
from cloudshell.cumulus.linux.command_actions.snmp import (
    BaseSnmpActions,
    SnmpV2Actions,
    SnmpV3Actions,
)
from cloudshell.cumulus.linux.command_actions.system import SystemActions
from cloudshell.cumulus.linux.snmp.snmp_conf_handler import SnmpConfigHandler

SNMP_PARAM_TYPES = Union[SNMPReadParameters, SNMPWriteParameters, SNMPV3Parameters]


class SnmpServerDown(BaseCumulusError):
    def __init__(self):
        super().__init__("SNMP server didn't started with a new config.")


class SnmpCommunityIsEmpty(BaseCumulusError):
    def __init__(self):
        super().__init__("SNMP community cannot be empty.")


@attr.s(auto_attribs=True, slots=True, frozen=True)
class CumulusEnableDisableSnmpFlow(EnableDisableSnmpFlowInterface):
    SNMP_WAITING_TIMEOUT: ClassVar[int] = 5 * 60
    SNMP_WAITING_INTERVAL: ClassVar[int] = 5

    _cli_configurator: CumulusCliConfigurator
    _resource_config: NetworkingResourceConfig
    _logger: Logger

    def enable_snmp(self, snmp_parameters: SNMP_PARAM_TYPES):
        if isinstance(snmp_parameters, SNMPV3Parameters):
            func = self._enable_snmp_v3
        else:
            func = self._enable_snmp_v2

        with self._cli_configurator.enable_mode_service() as cli_service:
            func(cli_service, snmp_parameters)

    def disable_snmp(self, snmp_parameters: SNMP_PARAM_TYPES):
        if isinstance(snmp_parameters, SNMPV3Parameters):
            func = self._disable_snmp_v3
        else:
            func = self._disable_snmp_v2

        with self._cli_configurator.enable_mode_service() as cli_service:
            func(cli_service, snmp_parameters)

    def _wait_for_snmp_service(self, snmp_act: BaseSnmpActions):
        timeout_time = datetime.now() + timedelta(seconds=self.SNMP_WAITING_TIMEOUT)

        while not snmp_act.is_snmp_running():
            if datetime.now() > timeout_time:
                msg = "SNMP Service didn't started after 'Enable SNMP' command"
                raise Exception(msg)
            self._logger.info("Waiting for SNMP service to start...")
            time.sleep(self.SNMP_WAITING_INTERVAL)

    def _enable_snmp_v3(
        self, cli_service: CliService, snmp_params: SNMPV3Parameters
    ) -> str:
        snmp_act = SnmpV3Actions(cli_service, self._logger)
        commit_act = CommitActions(cli_service, self._logger)

        try:
            if self._resource_config.vrf_management_name:
                output = snmp_act.add_listening_address_with_vrf(
                    self._resource_config.vrf_management_name,
                    self._resource_config.address,
                )
            else:
                output = snmp_act.add_listening_address()

            output += snmp_act.create_view()
            output += snmp_act.enable_snmp(
                snmp_user=snmp_params.snmp_user,
                snmp_password=snmp_params.snmp_password,
                snmp_priv_key=snmp_params.snmp_private_key,
                snmp_auth_proto=snmp_params.snmp_auth_protocol,
                snmp_priv_proto=snmp_params.snmp_private_key_protocol,
            )
            output += commit_act.commit()
        except CommandExecutionException:
            commit_act.abort()
            self._logger.exception("Failed to Enable SNMPv3 on the device")
            raise
        else:
            self._wait_for_snmp_service(snmp_act)
            return output

    def _enable_snmp_v2(
        self,
        cli_service: CliService,
        snmp_params: SNMPReadParameters | SNMPWriteParameters,
    ) -> str:
        if not snmp_params.snmp_community:
            raise Exception("SNMP community can not be empty")
        if isinstance(snmp_params, SNMPWriteParameters):
            raise Exception("Shell doesn't support SNMP v2 Read-write community")

        snmp_act = SnmpV2Actions(cli_service, self._logger)
        commit_act = CommitActions(cli_service, self._logger)

        try:
            if self._resource_config.vrf_management_name:
                output = snmp_act.add_listening_address_with_vrf(
                    self._resource_config.vrf_management_name,
                    self._resource_config.address,
                )
            else:
                output = snmp_act.add_listening_address()

            output += snmp_act.create_view()
            output += snmp_act.enable_snmp(snmp_params.snmp_community)
            output += commit_act.commit()
        except CommandExecutionException:
            self._logger.exception("Failed to Enable SNMPv2 on the device")
            commit_act.abort()
            raise

        self._wait_for_snmp_service(snmp_act)
        return output

    def _disable_snmp_v3(
        self, cli_service: CliService, snmp_params: SNMPV3Parameters
    ) -> str:
        snmp_act = SnmpV3Actions(cli_service, self._logger)
        commit_act = CommitActions(cli_service, self._logger)

        try:
            if self._resource_config.vrf_management_name:
                output = snmp_act.remove_listening_address_with_vrf(
                    self._resource_config.vrf_management_name,
                    self._resource_config.address,
                )
            else:
                output = snmp_act.remove_listening_address()

            output += snmp_act.disable_snmp(snmp_params.snmp_user)
            output += snmp_act.remove_view()
            output += commit_act.commit()
        except CommandExecutionException:
            commit_act.abort()
            self._logger.exception("Failed to Enable SNMPv3 on the device")
            raise

        return output

    def _disable_snmp_v2(
        self,
        cli_service: CliService,
        snmp_params: SNMPReadParameters | SNMPWriteParameters,
    ):
        if not snmp_params.snmp_community:
            raise Exception("SNMP community can not be empty")
        if isinstance(snmp_params, SNMPWriteParameters):
            raise Exception("Shell doesn't support SNMP v2 Read-write community")

        snmp_act = SnmpV2Actions(cli_service, self._logger)
        commit_act = CommitActions(cli_service, self._logger)

        try:
            if self._resource_config.vrf_management_name:
                output = snmp_act.remove_listening_address_with_vrf(
                    self._resource_config.vrf_management_name,
                    self._resource_config.address,
                )
            else:
                output = snmp_act.remove_listening_address()

            output += snmp_act.disable_snmp(snmp_params.snmp_community)
            output += snmp_act.remove_view()
            output += commit_act.commit()
        except CommandExecutionException:
            self._logger.exception("Failed to Enable SNMPv2 on the device:")
            commit_act.abort()
            raise

        return output


@attr.s(auto_attribs=True, slots=True, frozen=True)
class EnableDisableFlowWithConfig(EnableDisableSnmpFlowInterface):
    SNMP_WAITING_TIMEOUT: ClassVar[int] = 5 * 60
    SNMP_WAITING_INTERVAL: ClassVar[int] = 5

    _cli_configurator: CumulusCliConfigurator
    _resource_config: NetworkingResourceConfig
    _logger: Logger

    def enable_snmp(self, snmp_parameters: SNMP_PARAM_TYPES):
        self._validate_snmp_params(snmp_parameters)

        with self._cli_configurator.root_mode_service() as cli_service:
            r_conf = self._resource_config
            sys_act = SystemActions(cli_service, self._logger)
            snmp_act = BaseSnmpActions(cli_service, self._logger)
            snmp_conf = SnmpConfigHandler(sys_act.get_snmp_conf())

            snmp_conf.add_server_ip(r_conf.address, r_conf.vrf_management_name)
            snmp_conf.create_view()

            if isinstance(snmp_parameters, SNMPWriteParameters):
                snmp_conf.add_rw_community(snmp_parameters.snmp_community)
            elif isinstance(snmp_parameters, SNMPReadParameters):
                snmp_conf.add_ro_community(snmp_parameters.snmp_community)
            elif isinstance(snmp_parameters, SNMPV3Parameters):
                snmp_conf.create_user(
                    snmp_parameters.snmp_user,
                    snmp_parameters.snmp_auth_protocol,
                    snmp_parameters.snmp_password,
                    snmp_parameters.snmp_private_key_protocol,
                    snmp_parameters.snmp_private_key,
                )
            new_conf = snmp_conf.get_new_conf()
            sys_act.upload_snmp_conf(new_conf)

            is_server_started = snmp_act.is_snmp_running()
            if not is_server_started:
                sys_act.start_snmp_server()
            else:
                sys_act.restart_snmp_server()

            try:
                self._wait_for_snmp_service(snmp_act)
            except SnmpServerDown:
                msg = f"Failed to start the SNMP server with a new config:\n{new_conf}"
                self._logger.exception(msg)
                self._logger.info("Return old config file.")
                sys_act.upload_snmp_conf(snmp_conf.orig_text)
                if is_server_started:
                    sys_act.restart_snmp_server()
                raise

    def disable_snmp(self, snmp_parameters: SNMP_PARAM_TYPES):
        self._validate_snmp_params(snmp_parameters)

        with self._cli_configurator.root_mode_service() as cli_service:
            r_conf = self._resource_config
            sys_act = SystemActions(cli_service, self._logger)
            snmp_conf = SnmpConfigHandler(sys_act.get_snmp_conf())

            snmp_conf.remove_server_ip(r_conf.address, r_conf.vrf_management_name)
            snmp_conf.remove_view()

            if isinstance(snmp_parameters, SNMPWriteParameters):
                snmp_conf.remove_rw_community(snmp_parameters.snmp_community)
            elif isinstance(snmp_parameters, SNMPReadParameters):
                snmp_conf.remove_ro_community(snmp_parameters.snmp_community)
            elif isinstance(snmp_parameters, SNMPV3Parameters):
                snmp_conf.remove_user(snmp_parameters.snmp_user)

            new_conf = snmp_conf.get_new_conf()
            sys_act.upload_snmp_conf(new_conf)
            sys_act.stop_snmp_server()

    def _wait_for_snmp_service(self, snmp_act: BaseSnmpActions):
        timeout_time = datetime.now() + timedelta(seconds=self.SNMP_WAITING_TIMEOUT)

        while not snmp_act.is_snmp_running():
            if datetime.now() > timeout_time:
                raise SnmpServerDown()
            self._logger.info("Waiting for SNMP service to start...")
            time.sleep(self.SNMP_WAITING_INTERVAL)

    @staticmethod
    def _validate_snmp_params(params: SNMP_PARAM_TYPES):
        if isinstance(params, (SNMPReadParameters, SNMPWriteParameters)):
            if not params.snmp_community:
                raise SnmpCommunityIsEmpty()
