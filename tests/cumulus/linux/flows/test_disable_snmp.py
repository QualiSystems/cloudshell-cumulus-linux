import unittest

import mock

from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.cumulus.linux.flows.disable_snmp import CumulusLinuxDisableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV2ReadParameters
from cloudshell.snmp.snmp_parameters import SNMPV2WriteParameters
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters


class TestCumulusLinuxdisableSnmpFlow(unittest.TestCase):
    def setUp(self):
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.resource_config = mock.MagicMock()
        self.disable_snmp_flow = CumulusLinuxDisableSnmpFlow(cli_handler=self.cli_handler,
                                                             resource_config=self.resource_config,
                                                             logger=self.logger)

    def test_execute_flow_calls_disable_snmp_v2(self):
        """Check that method will call "_disable_snmp_v2" method if snmp_parameters is SNMP v2"""
        snmp_parameters = SNMPV2ReadParameters(ip="10.10.10.10",
                                               snmp_read_community="cumuluslinux")

        cli_service = mock.MagicMock()
        self.cli_handler.get_cli_service.return_value.__enter__.return_value = cli_service

        self.disable_snmp_flow._disable_snmp_v2 = mock.MagicMock()
        self.disable_snmp_flow._disable_snmp_v3 = mock.MagicMock()

        # act
        self.disable_snmp_flow.execute_flow(snmp_parameters=snmp_parameters)

        # verify
        self.disable_snmp_flow._disable_snmp_v2.assert_called_once_with(cli_service=cli_service,
                                                                        snmp_parameters=snmp_parameters)

    def test_execute_flow_calls_disable_snmp_v3(self):
        """Check that method will call "_disable_snmp_v3" method if snmp_parameters is SNMP v3"""
        snmp_parameters = SNMPV3Parameters(ip="10.10.10.10",
                                           snmp_user="testuser",
                                           snmp_password="testpassword",
                                           snmp_private_key="privkey")

        cli_service = mock.MagicMock()
        self.cli_handler.get_cli_service.return_value.__enter__.return_value = cli_service

        self.disable_snmp_flow._disable_snmp_v2 = mock.MagicMock()
        self.disable_snmp_flow._disable_snmp_v3 = mock.MagicMock()

        # act
        self.disable_snmp_flow.execute_flow(snmp_parameters=snmp_parameters)

        # verify
        self.disable_snmp_flow._disable_snmp_v3.assert_called_once_with(cli_service=cli_service,
                                                                        snmp_parameters=snmp_parameters)

    def test_disable_snmp_v2_will_raise_exception_in_case_of_empty_snmp_community_string(self):
        """Check that method will raise an Exception if snmp_parameters is an empty string"""
        snmp_parameters = SNMPV2ReadParameters(ip="10.10.10.10", snmp_read_community="")
        cli_service = mock.MagicMock()

        # act
        with self.assertRaisesRegexp(Exception, "SNMP community can not be empty"):
            self.disable_snmp_flow._disable_snmp_v2(cli_service=cli_service, snmp_parameters=snmp_parameters)

    def test_disable_snmp_v2_will_raise_exception_in_case_of_snmpv2_write_params(self):
        """Check that method will raise an Exception if snmp_parameters are SNMPV2WriteParameters"""
        snmp_parameters = SNMPV2WriteParameters(ip="10.10.10.10", snmp_write_community="test_write_community")
        cli_service = mock.MagicMock()

        with self.assertRaisesRegexp(Exception, "Shell doesn't support SNMP v2 Read-write community"):
            self.disable_snmp_flow._disable_snmp_v2(cli_service=cli_service, snmp_parameters=snmp_parameters)

    @mock.patch("cloudshell.cumulus.linux.flows.disable_snmp.CommitActions")
    @mock.patch("cloudshell.cumulus.linux.flows.disable_snmp.SnmpV2Actions")
    def test_disable_snmp_v2(self, snmp_action_class, commit_actions_class):
        """Check that method will call correct commands on SNMP and Commit actions"""
        snmp_parameters = mock.MagicMock()
        cli_service = mock.MagicMock()
        snmp_actions = mock.MagicMock()
        commit_actions = mock.MagicMock()
        snmp_action_class.return_value = snmp_actions
        commit_actions_class.return_value = commit_actions
        self.disable_snmp_flow._wait_for_snmp_service = mock.MagicMock()
        self.resource_config.vrf_management_name = ""
        # act
        self.disable_snmp_flow._disable_snmp_v2(cli_service=cli_service, snmp_parameters=snmp_parameters)
        # verify
        snmp_actions.remove_listening_address.assert_called_once_with()
        snmp_actions.remove_view.assert_called_once_with()
        snmp_actions.disable_snmp.assert_called_once_with(snmp_community=snmp_parameters.snmp_community)
        commit_actions.commit.assert_called_once_with()

    @mock.patch("cloudshell.cumulus.linux.flows.disable_snmp.CommitActions")
    @mock.patch("cloudshell.cumulus.linux.flows.disable_snmp.SnmpV2Actions")
    def test_disable_snmp_v2_with_vfr(self, snmp_action_class, commit_actions_class):
        """Check that method will call correct commands on SNMP and Commit actions"""
        snmp_parameters = mock.MagicMock()
        cli_service = mock.MagicMock()
        snmp_actions = mock.MagicMock()
        commit_actions = mock.MagicMock()
        snmp_action_class.return_value = snmp_actions
        commit_actions_class.return_value = commit_actions
        self.disable_snmp_flow._wait_for_snmp_service = mock.MagicMock()
        # act
        self.disable_snmp_flow._disable_snmp_v2(cli_service=cli_service, snmp_parameters=snmp_parameters)
        # verify
        snmp_actions.remove_listening_address_with_vrf.assert_called_once_with(
            vrf_management_name=self.resource_config.vrf_management_name,
            ip_address=self.resource_config.address)

        snmp_actions.remove_view.assert_called_once_with()
        snmp_actions.disable_snmp.assert_called_once_with(snmp_community=snmp_parameters.snmp_community)
        commit_actions.commit.assert_called_once_with()

    @mock.patch("cloudshell.cumulus.linux.flows.disable_snmp.CommitActions")
    @mock.patch("cloudshell.cumulus.linux.flows.disable_snmp.SnmpV3Actions")
    def test_disable_snmp_v3(self, snmp_action_class, commit_actions_class):
        """Check that method will call correct commands on SNMP and Commit actions"""
        snmp_parameters = mock.MagicMock()
        cli_service = mock.MagicMock()
        snmp_actions = mock.MagicMock()
        commit_actions = mock.MagicMock()
        snmp_action_class.return_value = snmp_actions
        commit_actions_class.return_value = commit_actions
        self.disable_snmp_flow._wait_for_snmp_service = mock.MagicMock()
        self.resource_config.vrf_management_name = ""
        # act
        self.disable_snmp_flow._disable_snmp_v3(cli_service=cli_service, snmp_parameters=snmp_parameters)
        # verify
        snmp_actions.remove_listening_address.assert_called_once_with()
        snmp_actions.remove_view.assert_called_once_with()
        snmp_actions.disable_snmp.assert_called_once_with(snmp_user=snmp_parameters.snmp_user)
        commit_actions.commit.assert_called_once_with()

    @mock.patch("cloudshell.cumulus.linux.flows.disable_snmp.CommitActions")
    @mock.patch("cloudshell.cumulus.linux.flows.disable_snmp.SnmpV3Actions")
    def test_disable_snmp_v3_with_vfr(self, snmp_action_class, commit_actions_class):
        """Check that method will call correct commands on SNMP and Commit actions"""
        snmp_parameters = mock.MagicMock()
        cli_service = mock.MagicMock()
        snmp_actions = mock.MagicMock()
        commit_actions = mock.MagicMock()
        snmp_action_class.return_value = snmp_actions
        commit_actions_class.return_value = commit_actions
        self.disable_snmp_flow._wait_for_snmp_service = mock.MagicMock()
        # act
        self.disable_snmp_flow._disable_snmp_v3(cli_service=cli_service, snmp_parameters=snmp_parameters)
        # verify
        snmp_actions.remove_listening_address_with_vrf.assert_called_once_with(
            vrf_management_name=self.resource_config.vrf_management_name,
            ip_address=self.resource_config.address)

        snmp_actions.remove_view.assert_called_once_with()
        snmp_actions.disable_snmp.assert_called_once_with(snmp_user=snmp_parameters.snmp_user)
        commit_actions.commit.assert_called_once_with()

    @mock.patch("cloudshell.cumulus.linux.flows.disable_snmp.CommitActions")
    @mock.patch("cloudshell.cumulus.linux.flows.disable_snmp.SnmpV2Actions")
    def test_disable_snmp_v2_method_will_call_abort_command_in_case_of_failure(self, snmp_action_class,
                                                                               commit_actions_class):
        """Check that method will call "abort" command in case of failed "commit" command"""
        snmp_parameters = mock.MagicMock()
        cli_service = mock.MagicMock()
        snmp_actions = mock.MagicMock()
        commit_actions = mock.MagicMock()
        snmp_action_class.return_value = snmp_actions
        commit_actions_class.return_value = commit_actions
        commit_actions.commit.side_effect = CommandExecutionException

        # act
        with self.assertRaises(CommandExecutionException):
            self.disable_snmp_flow._disable_snmp_v2(cli_service=cli_service, snmp_parameters=snmp_parameters)

        # verify
        commit_actions.abort.assert_called_once_with()

    @mock.patch("cloudshell.cumulus.linux.flows.disable_snmp.CommitActions")
    @mock.patch("cloudshell.cumulus.linux.flows.disable_snmp.SnmpV3Actions")
    def test_disable_snmp_v3_method_will_call_abort_command_in_case_of_failure(self, snmp_action_class,
                                                                               commit_actions_class):
        """Check that method will call "abort" command in case of failed "commit" command"""
        snmp_parameters = mock.MagicMock()
        cli_service = mock.MagicMock()
        snmp_actions = mock.MagicMock()
        commit_actions = mock.MagicMock()
        snmp_action_class.return_value = snmp_actions
        commit_actions_class.return_value = commit_actions
        commit_actions.commit.side_effect = CommandExecutionException

        # act
        with self.assertRaises(CommandExecutionException):
            self.disable_snmp_flow._disable_snmp_v3(cli_service=cli_service, snmp_parameters=snmp_parameters)

        # verify
        commit_actions.abort.assert_called_once_with()
