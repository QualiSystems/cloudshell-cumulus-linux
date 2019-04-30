from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.cumulus.linux.command_actions.commit import CommitActions
from cloudshell.cumulus.linux.command_actions.vlan import VLANActions
from cloudshell.devices.flows.cli_action_flows import RemoveVlanFlow


class CumulusLinuxRemoveVlanFlow(RemoveVlanFlow):

    @staticmethod
    def _get_port_name(full_port_name):
        """

        :param full_port_name:
        :return:
        """
        return full_port_name.split("/")[-1]

    def execute_flow(self, vlan_range, port_name, port_mode, action_map=None, error_map=None):
        """

        :param vlan_range:
        :param port_name:
        :param port_mode:
        :param action_map:
        :param error_map:
        :return:
        """
        port = self._get_port_name(full_port_name=port_name)

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as cli_service:
            vlan_actions = VLANActions(cli_service=cli_service, logger=self._logger)
            commit_actions = CommitActions(cli_service=cli_service, logger=self._logger)

            try:
                output = vlan_actions.remove_port_from_bridge(port=port)

                if port_mode == "trunk":
                    output += vlan_actions.remove_trunk_vlan_on_port(port=port)
                else:
                    output += vlan_actions.remove_access_vlan_on_port(port=port)

                output += commit_actions.commit()

            except CommandExecutionException:
                self._logger.exception("Failed to remove VLAN:")
                commit_actions.abort()
                raise

        return output
