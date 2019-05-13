import unittest

import mock

from cloudshell.cumulus.linux.runners.configuration import CumulusLinuxConfigurationRunner


class TestCumulusLinuxAutoloadRunner(unittest.TestCase):
    def setUp(self):
        self.resource_config = mock.MagicMock()
        self.api = mock.MagicMock()
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.config_runner = CumulusLinuxConfigurationRunner(resource_config=self.resource_config,
                                                             api=self.api,
                                                             cli_handler=self.cli_handler,
                                                             logger=self.logger)

    def test_get_path_with_empty_file_path(self):
        """Check that method will create correct path"""
        self.resource_config.backup_location = "192.168.10.10"
        self.resource_config.backup_type = "ftp"
        self.resource_config.backup_user = "admin"
        self.resource_config.backup_password = "admin"
        # act
        result = self.config_runner.get_path(path="")
        # verify
        self.assertEqual(result, "ftp://admin:admin@192.168.10.10")

    def test_get_path_with_empty_file_path_and_filesystem_backup_location(self):
        """Check that method will create correct path"""
        self.resource_config.backup_location = "/home/cumulus/image.bin"
        self.resource_config.backup_type = self.config_runner.DEFAULT_FILE_SYSTEM
        self.resource_config.backup_user = "admin"
        self.resource_config.backup_password = "admin"
        # act
        result = self.config_runner.get_path(path="")
        # verify
        self.assertEqual(result, "file:///home/cumulus/image.bin")

    @mock.patch("cloudshell.cumulus.linux.runners.configuration.CumulusLinuxSaveFlow")
    def test_save_flow(self, save_flow_class):
        save_flow = mock.MagicMock()
        save_flow_class.return_value = save_flow
        # act
        result = self.config_runner.save_flow
        # verify
        self.assertEqual(result, save_flow)

    @mock.patch("cloudshell.cumulus.linux.runners.configuration.CumulusLinuxRestoreFlow")
    def test_restore_flow(self, restore_flow_class):
        restore_flow = mock.MagicMock()
        restore_flow_class.return_value = restore_flow
        # act
        result = self.config_runner.restore_flow
        # verify
        self.assertEqual(result, restore_flow)
