import unittest

import mock

from cloudshell.cumulus.linux.flows.shutdown import CumulusLinuxShutdownFlow


class TestCumulusLinuxShutdownFlow(unittest.TestCase):
    def setUp(self):
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.shutdown_flow = CumulusLinuxShutdownFlow(cli_handler=self.cli_handler, logger=self.logger)

    @mock.patch("cloudshell.cumulus.linux.flows.shutdown.StateActions")
    def test_execute_flow(self, state_actions_class):
        """Check that method will call correct commands on State actions"""
        state_actions = mock.MagicMock()
        state_actions_class.return_value = state_actions

        # act
        self.shutdown_flow.execute_flow()

        # verify
        state_actions.shutdown.assert_called_once_with()
