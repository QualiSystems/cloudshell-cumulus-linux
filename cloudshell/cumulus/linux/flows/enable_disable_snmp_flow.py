from __future__ import annotations

import time
from datetime import datetime, timedelta
from logging import Logger
from typing import TYPE_CHECKING, ClassVar, Union

import attr

from cloudshell.snmp.snmp_configurator import EnableDisableSnmpFlowInterface
from cloudshell.snmp.snmp_parameters import (
    SNMPReadParameters,
    SNMPV3Parameters,
    SNMPWriteParameters,
)

from cloudshell.cumulus.linux import BaseCumulusError
from cloudshell.cumulus.linux.cli.handler import CumulusCliConfigurator
from cloudshell.cumulus.linux.command_actions.snmp import BaseSnmpActions
from cloudshell.cumulus.linux.command_actions.system import SystemActions
from cloudshell.cumulus.linux.snmp.snmp_conf_handler import SnmpConfigHandler

if TYPE_CHECKING:
    from cloudshell.shell.standards.networking.resource_config import (
        NetworkingResourceConfig,
    )


SNMP_PARAM_TYPES = Union[SNMPReadParameters, SNMPWriteParameters, SNMPV3Parameters]


class SnmpServerDown(BaseCumulusError):
    def __init__(self):
        super().__init__("SNMP server didn't started with a new config.")


class SnmpCommunityIsEmpty(BaseCumulusError):
    def __init__(self):
        super().__init__("SNMP community cannot be empty.")


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
