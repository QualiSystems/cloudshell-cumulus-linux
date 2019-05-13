import unittest

import mock

from cloudshell.cumulus.linux.snmp.handler import CumulusLinuxSnmpHandler


class TestCumulusLinuxAutoloadRunner(unittest.TestCase):
    def setUp(self):
        self.resource_config = mock.MagicMock()
        self.api = mock.MagicMock()
        self.cli_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.snmp_handler = CumulusLinuxSnmpHandler(resource_config=self.resource_config,
                                                    api=self.api,
                                                    cli_handler=self.cli_handler,
                                                    logger=self.logger)

    @mock.patch("cloudshell.cumulus.linux.snmp.handler.CumulusLinuxEnableSnmpFlow")
    def test_create_enable_flow(self, enable_snmp_flow_class):
        enable_snmp_flow = mock.MagicMock()
        enable_snmp_flow_class.return_value = enable_snmp_flow
        # act
        result = self.snmp_handler._create_enable_flow()
        # verify
        self.assertEqual(result, enable_snmp_flow)

    @mock.patch("cloudshell.cumulus.linux.snmp.handler.CumulusLinuxDisableSnmpFlow")
    def test_create_enable_flow(self, disable_snmp_flow_class):
        disable_snmp_flow = mock.MagicMock()
        disable_snmp_flow_class.return_value = disable_snmp_flow
        # act
        result = self.snmp_handler._create_disable_flow()
        # verify
        self.assertEqual(result, disable_snmp_flow)
