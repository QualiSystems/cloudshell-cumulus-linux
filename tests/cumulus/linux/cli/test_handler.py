import unittest

import mock

from cloudshell.cumulus.linux.cli.handler import CumulusCliHandler


class TestCliHandlerImpl(unittest.TestCase):
    def setUp(self):
        self.cli = mock.MagicMock()
        self.resource_config = mock.MagicMock()
        self.logger = mock.MagicMock()
        self.api = mock.MagicMock()
        self.cli_handler = CumulusCliHandler(cli=self.cli,
                                             resource_config=self.resource_config,
                                             api=self.api,
                                             logger=self.logger)

    