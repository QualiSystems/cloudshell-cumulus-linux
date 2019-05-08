import unittest

import mock

from cloudshell.cumulus.linux.flows.save import CumulusLinuxSaveFlow


class TestCumulusLinuxLoadFirmwareFlow(unittest.TestCase):
    def setUp(self):
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.save_flow = CumulusLinuxSaveFlow(cli_handler=self.cli_handler, logger=self.logger)

    @mock.patch("cloudshell.cumulus.linux.flows.save.SystemActions")
    def test_execute_flow(self, system_actions_class):
        """Check that method will call correct commands on System actions"""
        folder_path = mock.MagicMock()
        configuration_type = mock.MagicMock()
        vrf_management_name = mock.MagicMock()
        system_actions = mock.MagicMock()
        system_actions_class.return_value = system_actions

        # act
        self.save_flow.execute_flow(folder_path=folder_path,
                                    configuration_type=configuration_type,
                                    vrf_management_name=vrf_management_name)
        # verify
        system_actions.create_tmp_dir.assert_called_once_with()
        system_actions.copy_folder.assert_called()
        system_actions.copy_file.assert_called()
        system_actions.create_tmp_dir.assert_called_once_with()
        system_actions.tar_compress_folder.assert_called_once_with(compress_name=system_actions.create_tmp_file(),
                                                                   folder=system_actions.create_tmp_dir())

        system_actions.curl_upload_file.assert_called_once_with(file_path=system_actions.create_tmp_file(),
                                                                remote_url=folder_path)
