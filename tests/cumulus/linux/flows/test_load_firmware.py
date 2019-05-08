import unittest

import mock

from cloudshell.cumulus.linux.flows.load_firmware import CumulusLinuxLoadFirmwareFlow


class TestCumulusLinuxLoadFirmwareFlow(unittest.TestCase):
    def setUp(self):
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.load_firmware_flow = CumulusLinuxLoadFirmwareFlow(cli_handler=self.cli_handler, logger=self.logger)

    @mock.patch("cloudshell.cumulus.linux.flows.load_firmware.FirmwareActions")
    @mock.patch("cloudshell.cumulus.linux.flows.load_firmware.SystemActions")
    def test_execute_flow(self, system_actions_class, firmware_actions_class):
        """Check that method will call correct commands on Firmware and System actions"""
        path = mock.MagicMock()
        vrf = mock.MagicMock()
        timeout = mock.MagicMock()
        system_actions = mock.MagicMock()
        firmware_actions = mock.MagicMock()
        system_actions_class.return_value = system_actions
        firmware_actions_class.return_value = firmware_actions
        system_actions_class.reboot.side_effect = Exception

        cli_service = mock.MagicMock()
        self.cli_handler.get_cli_service.return_value.__enter__.return_value = cli_service

        # act
        self.load_firmware_flow.execute_flow(path=path, vrf=vrf, timeout=timeout)

        # verify
        firmware_actions.load_firmware.assert_called_once_with(image_path=path, timeout=timeout)
        system_actions.reboot.assert_called_once_with()
        cli_service.reconnect.assert_called_once_with(timeout)
