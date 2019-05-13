import unittest

import mock

from cloudshell.cumulus.linux.runners.autoload import CumulusLinuxAutoloadRunner


class TestCumulusLinuxAutoloadRunner(unittest.TestCase):
    def setUp(self):
        self.resource_config = mock.MagicMock()
        self.snmp_handler = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.autoload_runner = CumulusLinuxAutoloadRunner(resource_config=self.resource_config,
                                                          snmp_handler=self.snmp_handler,
                                                          logger=self.logger)

    @mock.patch("cloudshell.cumulus.linux.runners.autoload.CumulusLinuxSnmpAutoloadFlow")
    def test_autoload_flow(self, autoload_flow_class):
        autoload_flow = mock.MagicMock()
        autoload_flow_class.return_value = autoload_flow
        # act
        result = self.autoload_runner.autoload_flow
        # verify
        self.assertEqual(result, autoload_flow)
