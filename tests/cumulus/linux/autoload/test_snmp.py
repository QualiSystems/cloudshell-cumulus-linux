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

    @mock.patch("cloudshell.cumulus.linux.autoload.snmp.re")
    def test_is_valid_device_os_returns_true(self, re):
        supported_os = mock.MagicMock()
        re.search.return_value = True
        # act
        result = self.snmp_autoload._is_valid_device_os(supported_os=supported_os)
        # verify
        self.assertTrue(result)

    @mock.patch("cloudshell.cumulus.linux.autoload.snmp.re")
    def test_is_valid_device_os_returns_false(self, re):
        supported_os = mock.MagicMock()
        re.search.return_value = False
        # act
        result = self.snmp_autoload._is_valid_device_os(supported_os=supported_os)
        # verify
        self.assertFalse(result)

    @mock.patch("cloudshell.cumulus.linux.autoload.snmp.re")
    def test_get_device_model(self, re):
        # re.search.return_value = True
        # act
        result = self.snmp_autoload._get_device_model()
        # verify
        self.assertEquals(result, re.search().group())

    @mock.patch("cloudshell.cumulus.linux.autoload.snmp.re")
    def test_get_device_model_empty(self, re):
        re.search.return_value = None
        # act
        result = self.snmp_autoload._get_device_model()
        # verify
        self.assertEquals(result, "")

    @mock.patch("cloudshell.cumulus.linux.autoload.snmp.get_device_name")
    @mock.patch("cloudshell.cumulus.linux.autoload.snmp.re")
    def test_get_device_model_name(self, re, get_device_name):
        device_model = "test device model"
        # act
        result = self.snmp_autoload._get_device_model_name(device_model=device_model)
        # verify
        self.assertEquals(result, get_device_name())

    def test_get_device_os_version(self):
        version = "2.5.4"
        self.snmp_handler.get_property.return_value = "Cumulus Linux {} running on quanta lb9".format(version)
        # act
        result = self.snmp_autoload._get_device_os_version()
        # verify
        self.assertEquals(result, version)

    def test_get_device_details(self):
        self.snmp_autoload._get_device_os_version = mock.MagicMock()
        self.snmp_autoload._get_device_model = mock.MagicMock()
        self.snmp_autoload._get_device_model_name = mock.MagicMock()
        # act
        self.snmp_autoload._get_device_details()
        # verify
        self.assertEquals(self.snmp_autoload.resource.os_version, self.snmp_autoload._get_device_os_version())
        self.assertEquals(self.snmp_autoload.resource.model, self.snmp_autoload._get_device_model())
        self.assertEquals(self.snmp_autoload.resource.model_name, self.snmp_autoload._get_device_model_name())

    def test_load_cisco_mib(self):
        self.snmp_handler = mock.MagicMock()
        # act
        self.snmp_autoload.load_cisco_mib()
        # verify
        self.snmp_handler.update_mib_sources.called_once()
