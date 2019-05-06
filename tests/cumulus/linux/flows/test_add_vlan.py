import unittest

import mock

from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.cumulus.linux.flows.add_vlan import CumulusLinuxAddVlanFlow


class TestCumulusLinuxAddVlanFlow(unittest.TestCase):
    def setUp(self):
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.add_vlan_flow = CumulusLinuxAddVlanFlow(cli_handler=self.cli_handler, logger=self.logger)

    def test_get_port_name(self):
        port_name = "swp45"
        full_port_name = "Cumulus Linux/Chassis 1/{}".format(port_name)
        # act
        result = self.add_vlan_flow._get_port_name(full_port_name=full_port_name)
        # verify
        self.assertEqual(result, port_name)

    def test_execute_flow_method_raises_exception_for_q_in_q(self):
        """Check that method will raise exception in case of Q-in-Q port mode"""
        with self.assertRaisesRegexp(Exception, "Shell doesn't support QinQ"):
            self.add_vlan_flow.execute_flow(vlan_range="300-400",
                                            port_name="swp49",
                                            port_mode="access",
                                            qnq=True,
                                            c_tag="200")

    @mock.patch("cloudshell.cumulus.linux.flows.add_vlan.CommitActions")
    @mock.patch("cloudshell.cumulus.linux.flows.add_vlan.VLANActions")
    def test_execute_flow_method_in_access_mode(self, vlan_actions_class, commit_actions_class):
        """Check that method will call correct commands on VLAN and Commit actions"""
        vlan_actions = mock.MagicMock()
        commit_actions = mock.MagicMock()
        vlan_actions_class.return_value = vlan_actions
        commit_actions_class.return_value = commit_actions
        port = "swp49"
        vlan_range = "300-400"
        self.add_vlan_flow._get_port_name = mock.MagicMock(return_value=port)

        # act
        self.add_vlan_flow.execute_flow(vlan_range=vlan_range,
                                        port_name=mock.MagicMock(),
                                        port_mode="access",
                                        qnq=False,
                                        c_tag="200")
        # verify
        vlan_actions.add_port_to_bridge.assert_called_once_with(port=port)
        vlan_actions.add_access_vlan_to_port.assert_called_once_with(port=port, vlan=vlan_range)
        commit_actions.commit.assert_called_once_with()

    @mock.patch("cloudshell.cumulus.linux.flows.add_vlan.CommitActions")
    @mock.patch("cloudshell.cumulus.linux.flows.add_vlan.VLANActions")
    def test_execute_flow_method_in_trunk_mode(self, vlan_actions_class, commit_actions_class):
        """Check that method will call correct commands on VLAN and Commit actions"""
        vlan_actions = mock.MagicMock()
        commit_actions = mock.MagicMock()
        vlan_actions_class.return_value = vlan_actions
        commit_actions_class.return_value = commit_actions
        port = "swp49"
        vlan_range = "300-400"
        self.add_vlan_flow._get_port_name = mock.MagicMock(return_value=port)

        # act
        self.add_vlan_flow.execute_flow(vlan_range=vlan_range,
                                        port_name=mock.MagicMock(),
                                        port_mode="trunk",
                                        qnq=False,
                                        c_tag="200")
        # verify
        vlan_actions.add_port_to_bridge.assert_called_once_with(port=port)
        vlan_actions.allow_trunk_vlans_on_port.assert_called_once_with(port=port, vlan_range=vlan_range)
        commit_actions.commit.assert_called_once_with()

    @mock.patch("cloudshell.cumulus.linux.flows.add_vlan.CommitActions")
    @mock.patch("cloudshell.cumulus.linux.flows.add_vlan.VLANActions")
    def test_execute_flow_method_will_call_abort_command_in_case_of_failure(self, vlan_actions_class,
                                                                            commit_actions_class):
        """Check that method will call "abort" command in case of failed "commit" command"""
        vlan_actions = mock.MagicMock()
        commit_actions = mock.MagicMock()
        vlan_actions_class.return_value = vlan_actions
        commit_actions_class.return_value = commit_actions
        port = "swp49"
        vlan_range = "300-400"
        self.add_vlan_flow._get_port_name = mock.MagicMock(return_value=port)
        commit_actions.commit.side_effect = CommandExecutionException

        # act
        with self.assertRaises(CommandExecutionException):
            self.add_vlan_flow.execute_flow(vlan_range=vlan_range,
                                            port_name=mock.MagicMock(),
                                            port_mode="trunk",
                                            qnq=False,
                                            c_tag="200")
        # verify
        commit_actions.abort.assert_called_once_with()
