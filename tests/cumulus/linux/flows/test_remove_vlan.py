import unittest

import mock

from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.cumulus.linux.flows.remove_vlan import CumulusLinuxRemoveVlanFlow


class TestCumulusLinuxRemoveVlanFlow(unittest.TestCase):
    def setUp(self):
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.remove_vlan_flow = CumulusLinuxRemoveVlanFlow(cli_handler=self.cli_handler, logger=self.logger)

    def test_get_port_name(self):
        port_name = "swp45"
        full_port_name = "Cumulus Linux/Chassis 1/{}".format(port_name)
        # act
        result = self.remove_vlan_flow._get_port_name(full_port_name=full_port_name)
        # verify
        self.assertEqual(result, port_name)

    @mock.patch("cloudshell.cumulus.linux.flows.remove_vlan.CommitActions")
    @mock.patch("cloudshell.cumulus.linux.flows.remove_vlan.VLANActions")
    def test_execute_flow_method_in_access_mode(self, vlan_action_class, commit_actions_class):
        """Check that method will call correct commands on VLAN and Commit actions"""
        vlan_action = mock.MagicMock()
        commit_actions = mock.MagicMock()
        vlan_action_class.return_value = vlan_action
        commit_actions_class.return_value = commit_actions
        port = "swp49"
        vlan_range = "300-400"
        self.remove_vlan_flow._get_port_name = mock.MagicMock(return_value=port)

        # act
        self.remove_vlan_flow.execute_flow(vlan_range=vlan_range,
                                           port_name=mock.MagicMock(),
                                           port_mode="access")
        # verify
        vlan_action.remove_port_from_bridge.assert_called_once_with(port=port)
        vlan_action.remove_access_vlan_on_port.assert_called_once_with(port=port)
        commit_actions.commit.assert_called_once_with()

    @mock.patch("cloudshell.cumulus.linux.flows.remove_vlan.CommitActions")
    @mock.patch("cloudshell.cumulus.linux.flows.remove_vlan.VLANActions")
    def test_execute_flow_method_in_trunk_mode(self, vlan_action_class, commit_actions_class):
        """Check that method will call correct commands on VLAN and Commit actions"""
        vlan_action = mock.MagicMock()
        commit_actions = mock.MagicMock()
        vlan_action_class.return_value = vlan_action
        commit_actions_class.return_value = commit_actions
        port = "swp49"
        vlan_range = "300-400"
        self.remove_vlan_flow._get_port_name = mock.MagicMock(return_value=port)

        # act
        self.remove_vlan_flow.execute_flow(vlan_range=vlan_range,
                                           port_name=mock.MagicMock(),
                                           port_mode="trunk")
        # verify
        vlan_action.remove_port_from_bridge.assert_called_once_with(port=port)
        vlan_action.remove_trunk_vlan_on_port.assert_called_once_with(port=port)
        commit_actions.commit.assert_called_once_with()

    @mock.patch("cloudshell.cumulus.linux.flows.remove_vlan.CommitActions")
    @mock.patch("cloudshell.cumulus.linux.flows.remove_vlan.VLANActions")
    def test_execute_flow_method_will_call_abort_command_in_case_of_failure(self, vlan_action_class,
                                                                            commit_actions_class):
        """Check that method will call "abort" command in case of failed "commit" command"""
        vlan_action = mock.MagicMock()
        commit_actions = mock.MagicMock()
        vlan_action_class.return_value = vlan_action
        commit_actions_class.return_value = commit_actions
        port = "swp49"
        vlan_range = "300-400"
        self.remove_vlan_flow._get_port_name = mock.MagicMock(return_value=port)
        commit_actions.commit.side_effect = CommandExecutionException

        # act
        with self.assertRaises(CommandExecutionException):
            self.remove_vlan_flow.execute_flow(vlan_range=vlan_range,
                                               port_name=mock.MagicMock(),
                                               port_mode="trunk")
        # verify
        commit_actions.abort.assert_called_once_with()
