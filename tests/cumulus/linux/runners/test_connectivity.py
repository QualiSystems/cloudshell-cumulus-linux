import unittest

import mock

from cloudshell.cumulus.linux.runners.connectivity import CumulusLinuxConnectivityRunner


class TestCumulusLinuxConnectivityRunner(unittest.TestCase):
    def setUp(self):
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.connectivity_runner = CumulusLinuxConnectivityRunner(cli_handler=self.cli_handler,
                                                                  logger=self.logger)

    @mock.patch("cloudshell.cumulus.linux.runners.connectivity.CumulusLinuxAddVlanFlow")
    def test_add_vlan_flow(self, add_vlan_flow_class):
        add_vlan_flow = mock.MagicMock()
        add_vlan_flow_class.return_value = add_vlan_flow
        # act
        result = self.connectivity_runner.add_vlan_flow
        # verify
        self.assertEqual(result, add_vlan_flow)

    @mock.patch("cloudshell.cumulus.linux.runners.connectivity.CumulusLinuxRemoveVlanFlow")
    def test_remove_vlan_flow(self, remove_vlan_flow_class):
        remove_vlan_flow = mock.MagicMock()
        remove_vlan_flow_class.return_value = remove_vlan_flow
        # act
        result = self.connectivity_runner.remove_vlan_flow
        # verify
        self.assertEqual(result, remove_vlan_flow)
