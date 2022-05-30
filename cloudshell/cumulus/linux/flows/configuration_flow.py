from __future__ import annotations

from logging import Logger
from typing import TYPE_CHECKING

from cloudshell.shell.flows.configuration.basic_flow import (
    AbstractConfigurationFlow,
    ConfigurationType,
    RestoreMethod,
)
from cloudshell.shell.flows.utils.url import LocalFileURL

from cloudshell.cumulus.linux.cli.handler import CumulusCliConfigurator
from cloudshell.cumulus.linux.command_actions.system import SystemActions
from cloudshell.cumulus.linux.command_templates import CommandError

if TYPE_CHECKING:
    from cloudshell.shell.standards.networking.resource_config import (
        NetworkingResourceConfig,
    )


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
    LOCAL_URL_CLASS = LocalFileURL
    SUPPORTED_CONFIGURATION_TYPES = {ConfigurationType.RUNNING}
    SUPPORTED_RESTORE_METHODS = {RestoreMethod.OVERRIDE}

    def __init__(
        self,
        logger: Logger,
        resource_config: NetworkingResourceConfig,
        cli_configurator: CumulusCliConfigurator,
    ):
        super().__init__(logger, resource_config)
        self._cli_configurator = cli_configurator

    @property
    def file_system(self) -> str:
        return "file:/"

    def _save_flow(
        self,
        file_dst_url: ConfigurationFlow.REMOTE_URL_CLASS | LOCAL_URL_CLASS,
        configuration_type: ConfigurationType,
        vrf_management_name: str | None,
    ) -> str | None:
        with self._cli_configurator.root_mode_service() as cli_service:
            sys_act = SystemActions(cli_service, self._logger)
            backup_file = self._backup_to_tar_file(sys_act)
            self._logger.info(f"Uploading backup .tar archive '{backup_file}' via curl")
            if isinstance(file_dst_url, LocalFileURL):
                folder = file_dst_url.get_folder()
                sys_act.create_folder(folder)
            sys_act.curl_upload_file(
                file_path=backup_file, remote_url=str(file_dst_url)
            )
        return None

    def _restore_flow(
        self,
        config_path: ConfigurationFlow.REMOTE_URL_CLASS | LOCAL_URL_CLASS,
        configuration_type: ConfigurationType,
        restore_method: RestoreMethod,
        vrf_management_name: str | None,
    ) -> None:
        with self._cli_configurator.root_mode_service() as cli_service:
            sys_act = SystemActions(cli_service, self._logger)

            self._logger.info("Backup current state")
            backup_tar_file = self._backup_to_tar_file(sys_act)

            self._logger.info("Downloading backup files")
            backup_file = sys_act.create_tmp_file()
            sys_act.curl_download_file(
                remote_url=str(config_path), file_path=backup_file
            )
            self._logger.info("Start uncompress backup files to the system")
            sys_act.tar_uncompress_folder(backup_file, "/")

            try:
                self._restart_services(sys_act)
            except CommandError:
                self._logger.error(
                    "Failed to start services after restoring config. "
                    "Start rollback previous state"
                )
                sys_act.tar_uncompress_folder(backup_tar_file, "/")
                self._restart_services(sys_act)
                raise

    def _backup_to_tar_file(self, sys_act: SystemActions) -> str:
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
        return backup_file

    def _restart_services(self, sys_act: SystemActions):
        self._logger.info("Reloading all auto interfaces")
        sys_act.if_reload()
        for service in SERVICES_TO_RESTART:
            self._logger.info(f"Restarting '{service}' service")
            sys_act.restart_service(name=service)
