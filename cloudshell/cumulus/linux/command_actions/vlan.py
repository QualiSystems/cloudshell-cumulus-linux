from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.cumulus.linux.command_templates import add_remove_vlan


class VLANActions(object):
    def __init__(self, cli_service, logger):
        """

        :param cli_service:
        :param logger:
        """
        self._cli_service = cli_service
        self._logger = logger

    def add_port_to_bridge(self, port, action_map=None, error_map=None):
        """

        :param port:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=add_remove_vlan.ADD_PORT_TO_BRIDGE,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(port=port)

    def allow_trunk_vlans_on_port(self, port, vlan_range, action_map=None, error_map=None):
        """

        :param port:
        :param vlan_range:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=add_remove_vlan.ALLOW_TRUNK_VLAN_ON_PORT,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(port=port, vlan_range=vlan_range)

    def add_access_vlan_to_port(self, port, vlan, action_map=None, error_map=None):
        """

        :param port:
        :param vlan:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=add_remove_vlan.ADD_ACCESS_VLAN_TO_PORT,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(port=port, vlan=vlan)

    def remove_port_from_bridge(self, port, action_map=None, error_map=None):
        """

        :param port:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=add_remove_vlan.REMOVE_PORT_FROM_BRIDGE,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(port=port)

    def remove_trunk_vlan_on_port(self, port, action_map=None, error_map=None):
        """

        :param port:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=add_remove_vlan.REMOVE_TRUNK_VLAN_ON_PORT,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(port=port)

    def remove_access_vlan_on_port(self, port, action_map=None, error_map=None):
        """

        :param port:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(cli_service=self._cli_service,
                                       command_template=add_remove_vlan.REMOVE_ACCESS_VLAN_ON_PORT,
                                       action_map=action_map,
                                       error_map=error_map).execute_command(port=port)
