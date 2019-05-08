import unittest

import mock

from cloudshell.cumulus.linux.flows.autoload import CumulusLinuxSnmpAutoloadFlow


class TestCumulusLinuxSnmpAutoloadFlow(unittest.TestCase):
    def setUp(self):
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.autoload_flow = CumulusLinuxSnmpAutoloadFlow(snmp_handler=self.cli_handler, logger=self.logger)

    @mock.patch("cloudshell.cumulus.linux.flows.autoload.CumulusLinuxSNMPAutoload")
    def test_execute_flow(self, snmp_autoload_class):
        supported_os = mock.MagicMock()
        snmp_autoload = mock.MagicMock()
        snmp_autoload_class.return_value = snmp_autoload
        # act
        self.autoload_flow.execute_flow(supported_os=supported_os,
                                        shell_name=mock.MagicMock(),
                                        shell_type=mock.MagicMock(),
                                        resource_name=mock.MagicMock())
        # verify
        snmp_autoload.discover.assert_called_once_with(supported_os)
