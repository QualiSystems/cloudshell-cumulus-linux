from logging import Logger
from threading import Lock

from cloudshell.shell.flows.connectivity.basic_flow import AbstractConnectivityFlow
from cloudshell.shell.flows.connectivity.helpers.vlan_helper import get_vlan_list
from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectionModeEnum,
    ConnectivityActionModel,
)
from cloudshell.shell.flows.connectivity.models.driver_response import (
    ConnectivityActionResult,
)
from cloudshell.shell.flows.connectivity.parse_request_service import (
    AbstractParseConnectivityService,
)
from cloudshell.shell.standards.networking.resource_config import (
    NetworkingResourceConfig,
)

from cloudshell.cumulus.linux.cli.handler import CumulusCliConfigurator
from cloudshell.cumulus.linux.command_actions.system import SystemActions
from cloudshell.cumulus.linux.connectivity.vlan_config_handler import (
    VlanConfHandler,
    VlanQinqConfHandler,
)

lock = Lock()


class CumulusConnectivityFlow(AbstractConnectivityFlow):
    # Cumulus supports VLAN ranges and multiple VLANs
    def __init__(
        self,
        parse_connectivity_request_service: AbstractParseConnectivityService,
        logger: Logger,
        resource_config: NetworkingResourceConfig,
        cli_configurator: CumulusCliConfigurator,
    ):
        super().__init__(parse_connectivity_request_service, logger)
        self._resource_config = resource_config
        self._cli_configurator = cli_configurator

    @staticmethod
    def _get_port_name(action: ConnectivityActionModel) -> str:
        return action.action_target.name.split("/")[-1]

    def _set_vlan(self, action: ConnectivityActionModel) -> ConnectivityActionResult:
        vlan_str = action.connection_params.vlan_id
        port_name = self._get_port_name(action)

        with lock:
            with self._cli_configurator.root_mode_service() as cli_service:
                sys_actions = SystemActions(cli_service, self._logger)
                conf_text = sys_actions.get_iface_conf()
                if action.connection_params.vlan_service_attrs.qnq:
                    vlan_handler = VlanQinqConfHandler(conf_text)
                else:
                    vlan_handler = VlanConfHandler(conf_text)

                vlan_handler.prepare_bridge()
                if action.connection_params.mode is ConnectionModeEnum.ACCESS:
                    vlan_handler.add_access_vlan(port_name, vlan_str)
                else:
                    vlan_list = get_vlan_list(
                        vlan_str,
                        is_vlan_range_supported=False,
                        is_multi_vlan_supported=False,
                    )
                    vlan_handler.add_trunk_vlan(port_name, vlan_list)

                sys_actions.upload_iface_conf(vlan_handler.text)
                sys_actions.if_reload()
        return ConnectivityActionResult.success_result(action, "Success")

    def _remove_vlan(self, action: ConnectivityActionModel) -> ConnectivityActionResult:
        port_name = self._get_port_name(action)

        with lock:
            with self._cli_configurator.root_mode_service() as cli_service:
                sys_actions = SystemActions(cli_service, self._logger)
                conf_text = sys_actions.get_iface_conf()
                if action.connection_params.vlan_service_attrs.qnq:
                    vlan_handler = VlanQinqConfHandler(conf_text)
                else:
                    vlan_handler = VlanConfHandler(conf_text)

                if action.connection_params.mode is ConnectionModeEnum.ACCESS:
                    vlan_handler.remove_access_vlan(port_name)
                else:
                    vlan_handler.remove_trunk_vlan(port_name)

                sys_actions.upload_iface_conf(vlan_handler.text)
                sys_actions.if_reload()
        return ConnectivityActionResult.success_result(action, "Success")
