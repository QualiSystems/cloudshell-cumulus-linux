from __future__ import annotations

import os
from logging import Logger

from cloudshell.shell.flows.configuration.basic_flow import AbstractConfigurationFlow
from cloudshell.shell.standards.networking.resource_config import (
    NetworkingResourceConfig,
)

from cloudshell.cumulus.linux.cli.handler import CumulusCliConfigurator
from cloudshell.cumulus.linux.command_actions.system import SystemActions

CONF_FOLDERS = (
    "/etc/network/",
    "/etc/frr/",
    "/etc/cumulus/acl/*",
    "/etc/lldpd.d/",
    "/etc/ssh/",
)

CONF_FILES = (
    "/etc/resolv.conf",
    "/etc/cumulus/ports.conf",
    "/etc/cumulus/switchd.conf",
    "/etc/passwd",
    "/etc/shadow",
    "/etc/group",
    "/etc/lldpd.conf",
    "/etc/nsswitch.conf",
    "/etc/sudoers",
    "/etc/sudoers.d",
    "/etc/ntp.conf",
    "/etc/timezone",
    "/etc/snmp/snmpd.conf",
    "/etc/default/isc-dhcp-relay",
    "/etc/default/isc-dhcp-relay6",
    "/etc/default/isc-dhcp-server",
    "/etc/default/isc-dhcp-server6",
    "/etc/cumulus/ports.conf",
    "/etc/ptp4l.conf",
    "/etc/hostname",
    "/etc/vxsnd.conf",
    "/etc/hosts",
    "/etc/dhcp/dhclient-exit-hooks.d/dhcp-sethostname",
    "/usr/lib/python2.7/dist-packages/cumulus/__chip_config/mlx/datapath.conf",
    "/etc/cumulus/datapath/traffic.conf",
    "/etc/hostapd.conf",
    "/etc/security/limits.conf",
)

SERVICES_TO_RESTART = ("mstpd", "frr", "sshd", "lldpd", "switchd")


class ConfigurationFlow(AbstractConfigurationFlow):
    def __init__(
        self,
        logger: Logger,
        resource_config: NetworkingResourceConfig,
        cli_configurator: CumulusCliConfigurator,
    ):
        super().__init__(logger, resource_config)
        self._cli_configurator = cli_configurator

    @property
    def _file_system(self) -> str:
        return "file"

    def _save_flow(
        self, folder_path: str, configuration_type: str, vrf_management_name: str | None
    ) -> None:
        with self._cli_configurator.root_mode_service() as cli_service:
            sys_act = SystemActions(cli_service, self._logger)

            self._logger.info("Creating backup files")
            backup_dir = sys_act.create_tmp_dir()
            for conf_folder in CONF_FOLDERS:
                sys_act.copy_folder(src_folder=conf_folder, dst_folder=backup_dir)
            for conf_file in CONF_FILES:
                sys_act.copy_file(src_file=conf_file, dst_folder=backup_dir)

            self._logger.info(
                f"Compressing backup directory '{backup_dir}' to .tar archive"
            )
            backup_file = sys_act.create_tmp_file()
            sys_act.tar_compress_folder(compress_name=backup_file, folder=backup_dir)

            self._logger.info(f"Uploading backup .tar archive '{backup_file}' via curl")
            if folder_path.startswith(self._local_path):
                folder = self._get_folder_from_local_url(folder_path)
                sys_act.create_folder(folder)
            sys_act.curl_upload_file(file_path=backup_file, remote_url=folder_path)

    def _restore_flow(
        self,
        path: str,
        configuration_type: str,
        restore_method: str,
        vrf_management_name: str | None,
    ) -> None:
        with self._cli_configurator.root_mode_service() as cli_service:
            sys_act = SystemActions(cli_service, self._logger)

            self._logger.info("Downloading backup files")
            backup_file = sys_act.create_tmp_file()
            sys_act.curl_download_file(remote_url=path, file_path=backup_file)

            self._logger.info("Uncompressing backup files to the system")
            sys_act.tar_uncompress_folder(compressed_file=backup_file, destination="/")

            self._logger.info("Reloading all auto interfaces")
            sys_act.if_reload()

            for service in SERVICES_TO_RESTART:
                self._logger.info(f"Restarting '{service}' service")
                sys_act.restart_service(name=service)

    def _get_path(self, path: str = "") -> str:
        path = super()._get_path(path)
        path = self._update_local_path(path)
        return path

    @property
    def _local_path(self) -> str:
        return f"{self._file_system}://localhost/"

    def _update_local_path(self, path: str) -> str:
        if path.startswith(self._file_system) and not path.startswith(self._local_path):
            scheme_len = len(f"{self._file_system}://")
            path = f"{self._local_path}{path[scheme_len:]}"
        return path

    def _get_folder_from_local_url(self, path: str) -> str:
        return os.path.dirname(path[len(self._local_path) - 1 :])
