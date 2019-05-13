import unittest

import mock

from cloudshell.cumulus.linux.runners.state import CumulusLinuxStateRunner


class TestCumulusLinuxStateRunner(unittest.TestCase):
    def setUp(self):
        self.resource_config = mock.MagicMock()
        self.api = mock.MagicMock()
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.state_runner = CumulusLinuxStateRunner(resource_config=self.resource_config,
                                                    api=self.api,
                                                    cli_handler=self.cli_handler,
                                                    logger=self.logger)

    @mock.patch("cloudshell.cumulus.linux.runners.state.CumulusLinuxShutdownFlow")
    def test_shutdown_flow(self, shutdown_flow_class):
        shutdown_flow = mock.MagicMock()
        shutdown_flow_class.return_value = shutdown_flow
        # act
        result = self.state_runner.shutdown_flow
        # verify
        self.assertEqual(result, shutdown_flow)

    @mock.patch("cloudshell.cumulus.linux.runners.state.CumulusLinuxShutdownFlow")
    def test_shutdown(self, shutdown_flow_class):
        shutdown_flow = mock.MagicMock()
        shutdown_flow_class.return_value = shutdown_flow
        # act
        self.state_runner.shutdown()
        # verify
        shutdown_flow.execute_flow.assert_called_once_with()
