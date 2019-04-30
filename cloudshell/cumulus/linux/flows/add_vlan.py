from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.cumulus.linux.command_actions.commit import CommitActions
from cloudshell.cumulus.linux.command_actions.vlan import VLANActions
from cloudshell.devices.flows.cli_action_flows import AddVlanFlow


class CumulusLinuxAddVlanFlow(AddVlanFlow):

    @staticmethod
    def _get_port_name(full_port_name):
        """

        :param full_port_name:
        :return:
        """
        return full_port_name.split("/")[-1]

    def execute_flow(self, vlan_range, port_mode, port_name, qnq, c_tag):
        """

        :param vlan_range:
        :param port_mode:
        :param port_name:
        :param qnq:
        :param c_tag:
        :return:
        """
        port = self._get_port_name(full_port_name=port_name)

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as cli_service:
            vlan_actions = VLANActions(cli_service=cli_service, logger=self._logger)
            commit_actions = CommitActions(cli_service=cli_service, logger=self._logger)

            try:
                if qnq:
                    raise Exception("Shell doesn't support QinQ")

                output = vlan_actions.add_port_to_bridge(port=port)

                if port_mode == "trunk":
                    output += vlan_actions.allow_trunk_vlans_on_port(port=port, vlan_range=vlan_range)
                else:
                    output += vlan_actions.add_access_vlan_to_port(port=port, vlan=vlan_range)

                output += commit_actions.commit()

            except CommandExecutionException:
                self._logger.exception("Failed to add VLAN:")
                commit_actions.abort()
                raise

        return output
