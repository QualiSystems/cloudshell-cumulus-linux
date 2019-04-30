from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.cumulus.linux.command_templates import state


class StateActions(object):
    def __init__(self, cli_service, logger):
        """

        :param cli_service:
        :param logger:
        """
        self._cli_service = cli_service
        self._logger = logger

    def shutdown(self, action_map=None, error_map=None):
        """

        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=state.SHUTDOWN,
                                       action_map=action_map,
                                       error_map=error_map).execute_command()
