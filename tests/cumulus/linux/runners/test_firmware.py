import unittest

import mock

from cloudshell.cumulus.linux.runners.firmware import CumulusLinuxFirmwareRunner


class TestCumulusLinuxFirmwareRunner(unittest.TestCase):
    def setUp(self):
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.firmware_runner = CumulusLinuxFirmwareRunner(cli_handler=self.cli_handler,
                                                          logger=self.logger)

    @mock.patch("cloudshell.cumulus.linux.runners.firmware.CumulusLinuxLoadFirmwareFlow")
    def test_load_firmware_flow(self, load_firmware_flow_class):
        load_firmware_flow = mock.MagicMock()
        load_firmware_flow_class.return_value = load_firmware_flow
        # act
        result = self.firmware_runner.load_firmware_flow
        # verify
        self.assertEqual(result, load_firmware_flow)
