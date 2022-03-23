from __future__ import annotations

from logging import Logger

import attr

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.service.cli_service import CliService

from cloudshell.cumulus.linux.command_templates import system
from cloudshell.cumulus.linux.const import (
    IFACE_CONF_PATH,
    SNMP_CONF_PATH,
    SNMP_SERVICE_NAME,
)


@attr.s(auto_attribs=True, slots=True, frozen=True)
class SystemActions:
    _cli_service: CliService
    _logger: Logger

    def create_tmp_file(self) -> str:
        tmp_file = CommandTemplateExecutor(
            self._cli_service, system.CREATE_TEMP_FILE, remove_prompt=True
        ).execute_command()
        return tmp_file.rstrip()

    def create_tmp_dir(self) -> str:
        tmp_dir = CommandTemplateExecutor(
            self._cli_service, system.CREATE_TEMP_DIR, remove_prompt=True
        ).execute_command()
        return tmp_dir.rstrip()

    def create_folder(self, folder_path: str) -> str:
        return CommandTemplateExecutor(
            self._cli_service, system.CREATE_FOLDER
        ).execute_command(folder_path=folder_path)

    def copy_folder(
        self,
        src_folder: str,
        dst_folder: str,
    ) -> str:
        return CommandTemplateExecutor(
            self._cli_service, system.COPY_FOLDER
        ).execute_command(src_folder=src_folder, dst_folder=dst_folder)

    def copy_file(self, src_file: str, dst_folder: str) -> str:
        return CommandTemplateExecutor(
            self._cli_service, system.COPY_FILE
        ).execute_command(src_file=src_file, dst_folder=dst_folder)

    def tar_compress_folder(self, compress_name: str, folder: str) -> str:
        return CommandTemplateExecutor(
            self._cli_service, system.TAR_COMPRESS_FOLDER
        ).execute_command(compress_name=compress_name, folder=folder)

    def tar_uncompress_folder(self, compressed_file: str, destination: str) -> str:
        return CommandTemplateExecutor(
            self._cli_service, system.TAR_UNCOMPRESS_FOLDER
        ).execute_command(compressed_file=compressed_file, destination=destination)

    def curl_upload_file(self, file_path: str, remote_url: str) -> str:
        return CommandTemplateExecutor(
            self._cli_service, system.CURL_UPLOAD_FILE
        ).execute_command(file_path=file_path, remote_url=remote_url)

    def curl_download_file(self, remote_url: str, file_path: str) -> str:
        return CommandTemplateExecutor(
            self._cli_service, system.CURL_DOWNLOAD_FILE
        ).execute_command(remote_url=remote_url, file_path=file_path)

    def if_reload(self) -> str:
        return CommandTemplateExecutor(
            self._cli_service, system.IF_RELOAD
        ).execute_command()

    def restart_service(self, name: str) -> str:
        return CommandTemplateExecutor(
            self._cli_service, system.RESTART_SERVICE
        ).execute_command(name=name)

    def shutdown(self) -> None:
        CommandTemplateExecutor(self._cli_service, system.SHUTDOWN).execute_command()

    def reboot(self) -> str:
        return CommandTemplateExecutor(
            self._cli_service, system.REBOOT
        ).execute_command()

    def get_snmp_conf(self) -> str:
        return (
            CommandTemplateExecutor(
                self._cli_service, system.READ_FILE, remove_prompt=True
            )
            .execute_command(file_path=SNMP_CONF_PATH)
            .strip()
        )

    def upload_snmp_conf(self, text: str) -> None:
        CommandTemplateExecutor(self._cli_service, system.WRITE_FILE).execute_command(
            text=text, file_path=SNMP_CONF_PATH
        )

    def get_iface_conf(self) -> str:
        return (
            CommandTemplateExecutor(
                self._cli_service, system.READ_FILE, remove_prompt=True
            )
            .execute_command(file_path=IFACE_CONF_PATH)
            .strip()
        )

    def upload_iface_conf(self, text: str) -> None:
        CommandTemplateExecutor(self._cli_service, system.WRITE_FILE).execute_command(
            text=text, file_path=IFACE_CONF_PATH
        )

    def restart_snmp_server(self) -> None:
        self.restart_service(SNMP_SERVICE_NAME)

    def start_snmp_server(self) -> None:
        CommandTemplateExecutor(
            self._cli_service, system.START_SERVICE
        ).execute_command(name=SNMP_SERVICE_NAME)

    def stop_snmp_server(self) -> None:
        CommandTemplateExecutor(self._cli_service, system.STOP_SERVICE).execute_command(
            name=SNMP_SERVICE_NAME
        )
