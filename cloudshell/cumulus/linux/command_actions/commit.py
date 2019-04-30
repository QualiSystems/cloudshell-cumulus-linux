from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.cumulus.linux.command_templates import commit_abort


class CommitActions(object):
    COMMIT_COMMAND_TIMEOUT = 5 * 60
    ABORT_COMMAND_TIMEOUT = 5 * 60

    def __init__(self, cli_service, logger):
        """

        :param cli_service:
        :param logger:
        """
        self._cli_service = cli_service
        self._logger = logger

    def commit(self, action_map=None, error_map=None):
        """

        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=commit_abort.COMMIT,
                                       action_map=action_map,
                                       timeout=self.COMMIT_COMMAND_TIMEOUT,
                                       error_map=error_map).execute_command()

    def abort(self, action_map=None, error_map=None):
        """

        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=commit_abort.ABORT,
                                       timeout=self.ABORT_COMMAND_TIMEOUT,
                                       action_map=action_map,
                                       error_map=error_map).execute_command()
