import unittest

import mock

from cloudshell.cumulus.linux.flows.restore import CumulusLinuxRestoreFlow


class TestCumulusLinuxLoadFirmwareFlow(unittest.TestCase):
    def setUp(self):
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.restore_flow = CumulusLinuxRestoreFlow(cli_handler=self.cli_handler, logger=self.logger)

    @mock.patch("cloudshell.cumulus.linux.flows.restore.SystemActions")
    def test_execute_flow(self, system_actions_class):
        """Check that method will call correct commands on System actions"""
        path = mock.MagicMock()
        configuration_type = mock.MagicMock()
        restore_method = mock.MagicMock()
        vrf_management_name = mock.MagicMock()
        system_actions = mock.MagicMock()
        system_actions_class.return_value = system_actions

        # act
        self.restore_flow.execute_flow(path=path,
                                       configuration_type=configuration_type,
                                       restore_method=restore_method,
                                       vrf_management_name=vrf_management_name)
        # verify
        system_actions.create_tmp_file.assert_called_once_with()
        system_actions.curl_download_file.assert_called_once_with(file_path=system_actions.create_tmp_file(),
                                                                  remote_url=path)

        system_actions.tar_uncompress_folder.assert_called_once_with(compressed_file=system_actions.create_tmp_file(),
                                                                     destination='/')
        system_actions.if_reload.assert_called_once_with()
        system_actions.restart_service.assert_called()
