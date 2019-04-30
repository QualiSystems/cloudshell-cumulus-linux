from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.cumulus.linux.command_templates import system


class SystemActions(object):
    def __init__(self, cli_service, logger):
        """

        :param cli_service:
        :param logger:
        """
        self._cli_service = cli_service
        self._logger = logger

    def create_tmp_file(self, action_map=None, error_map=None):
        """

        :param action_map:
        :param error_map:
        :return:
        """
        tmp_file = CommandTemplateExecutor(cli_service=self._cli_service,
                                           command_template=system.CREATE_TEMP_FILE,
                                           action_map=action_map,
                                           remove_prompt=True,
                                           error_map=error_map).execute_command()

        return tmp_file.rstrip()

    def create_tmp_dir(self, action_map=None, error_map=None):
        """

        :param action_map:
        :param error_map:
        :return:
        """
        tmp_dir = CommandTemplateExecutor(cli_service=self._cli_service,
                                          command_template=system.CREATE_TEMP_DIR,
                                          action_map=action_map,
                                          remove_prompt=True,
                                          error_map=error_map).execute_command()

        return tmp_dir.rstrip()

    def copy_folder(self, src_folder, dst_folder, action_map=None, error_map=None):
        """

        :param src_folder:
        :param dst_folder:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=system.COPY_FOLDER,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(src_folder=src_folder,
                                                                            dst_folder=dst_folder)

    def copy_file(self, src_file, dst_folder, action_map=None, error_map=None):
        """

        :param src_file:
        :param dst_folder:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=system.COPY_FILE,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(src_file=src_file, dst_folder=dst_folder)

    def tar_compress_folder(self, compress_name, folder, action_map=None, error_map=None):
        """

        :param compress_name:
        :param folder:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=system.TAR_COMPRESS_FOLDER,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(compress_name=compress_name, folder=folder)

    def tar_uncompress_folder(self, compressed_file, destination, action_map=None, error_map=None):
        """

        :param compressed_file:
        :param destination:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=system.TAR_UNCOMPRESS_FOLDER,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(compressed_file=compressed_file,
                                                                            destination=destination)

    def curl_upload_file(self, file_path, remote_url, action_map=None, error_map=None):
        """

        :param file_path:
        :param remote_url:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=system.CURL_UPLOAD_FILE,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(file_path=file_path, remote_url=remote_url)

    def curl_download_file(self, remote_url, file_path, action_map=None, error_map=None):
        """

        :param remote_url:
        :param file_path:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=system.CURL_DOWNLOAD_FILE,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(remote_url=remote_url, file_path=file_path)

    def if_reload(self, action_map=None, error_map=None):
        """

        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=system.IF_RELOAD,
                                       action_map=action_map,
                                       error_map=error_map).execute_command()

    def restart_service(self, name, action_map=None, error_map=None):
        """

        :param name:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=system.RESTART_SERVICE,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(name=name)

    def reboot(self, action_map=None, error_map=None):
        """

        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=system.REBOOT,
                                       action_map=action_map,
                                       error_map=error_map).execute_command()
