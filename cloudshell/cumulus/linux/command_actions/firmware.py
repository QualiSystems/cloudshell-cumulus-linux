from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.cumulus.linux.command_templates import firmware


class FirmwareActions(object):
    def __init__(self, cli_service, logger):
        """

        :param cli_service:
        :param logger:
        """
        self._cli_service = cli_service
        self._logger = logger

    def load_firmware(self, image_path, timeout, action_map=None, error_map=None):
        """

        :param image_path:
        :param timeout:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=firmware.LOAD_FIRMWARE,
                                       action_map=action_map,
                                       timeout=timeout,
                                       error_map=error_map).execute_command(image_path=image_path)
