import unittest

import mock

from cloudshell.cumulus.linux.autoload.snmp import CumulusLinuxSNMPAutoload


class TestCumulusLinuxSNMPAutoload(unittest.TestCase):
    def setUp(self):
        self.snmp_handler = mock.MagicMock()
        self.resource_config = mock.MagicMock()
        self.shell_type = mock.MagicMock()
        self.resource_name = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.snmp_autoload = CumulusLinuxSNMPAutoload(snmp_handler=self.snmp_handler,
                                                      shell_name=self.resource_config,
                                                      shell_type="CS_Switch",
                                                      resource_name=self.resource_name,
                                                      logger=self.logger)

    @mock.patch("cloudshell.cumulus.linux.autoload.snmp.AutoloadDetailsBuilder")
    @mock.patch("cloudshell.cumulus.linux.autoload.snmp.CiscoSNMPEntityTable")
    def test_discover(self, snmp_entity_table_class, autoload_details_builder_class):
        supported_os = mock.MagicMock()
        self.snmp_autoload._is_valid_device_os = mock.MagicMock()
        self.snmp_autoload._get_device_os_version = mock.MagicMock()
        self.snmp_autoload._get_device_details = mock.MagicMock()
        # act
        result = self.snmp_autoload.discover(supported_os=supported_os)
        # verify
        self.assertEquals(result, autoload_details_builder_class().autoload_details())
