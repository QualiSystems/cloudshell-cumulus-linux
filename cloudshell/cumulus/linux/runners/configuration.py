import re

from cloudshell.cumulus.linux.flows.save import CumulusLinuxSaveFlow
from cloudshell.cumulus.linux.flows.restore import CumulusLinuxRestoreFlow
from cloudshell.devices.networking_utils import UrlParser
from cloudshell.devices.runners.configuration_runner import ConfigurationRunner


AUTHORIZATION_REQUIRED_STORAGE = ['ftp', 'sftp', 'scp']


class CumulusLinuxConfigurationRunner(ConfigurationRunner):

    def get_path(self, path=''):
        """

        :param path:
        :return:
        """
        if not path:
            host = self.resource_config.backup_location
            if ':' not in host:
                scheme = self.resource_config.backup_type
                if not scheme or scheme.lower() == self.DEFAULT_FILE_SYSTEM.lower():
                    scheme = self.file_system

                scheme = re.sub('(:|/+).*$', '', scheme, re.DOTALL)
                # todo: clarify and remove this line in networking-devices
                # host = re.sub('^/+', '', host)
                host = '{}://{}'.format(scheme, host)
            path = host

        url = UrlParser.parse_url(path)

        if url[UrlParser.SCHEME].lower() in AUTHORIZATION_REQUIRED_STORAGE:
            if UrlParser.USERNAME not in url or not url[UrlParser.USERNAME]:
                url[UrlParser.USERNAME] = self.resource_config.backup_user
            if UrlParser.PASSWORD not in url or not url[UrlParser.PASSWORD]:
                url[UrlParser.PASSWORD] = self.resource_config.backup_user
        try:
            result = UrlParser.build_url(url)
        except Exception as e:
            self._logger.error('Failed to build url: {}'.format(e))
            raise Exception('ConfigurationOperations', 'Failed to build path url to remote host')
        return result

    @property
    def save_flow(self):
        """

        :return:
        """
        return CumulusLinuxSaveFlow(cli_handler=self.cli_handler, logger=self._logger)

    @property
    def restore_flow(self):
        """

        :return:
        """
        return CumulusLinuxRestoreFlow(cli_handler=self.cli_handler, logger=self._logger)

    @property
    def file_system(self):
        """

        :return:
        """
        return "file://"
