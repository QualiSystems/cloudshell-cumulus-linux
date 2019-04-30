from datetime import datetime
from datetime import timedelta
import time

from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.cumulus.linux.command_actions.commit import CommitActions
from cloudshell.cumulus.linux.command_actions.snmp import SnmpV2Actions
from cloudshell.cumulus.linux.command_actions.snmp import SnmpV3Actions
from cloudshell.devices.flows.cli_action_flows import EnableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters
from cloudshell.snmp.snmp_parameters import SNMPV2WriteParameters


class CumulusLinuxEnableSnmpFlow(EnableSnmpFlow):
    SNMP_WAITING_TIMEOUT = 5 * 60
    SNMP_WAITING_INTERVAL = 5

    def execute_flow(self, snmp_parameters):
        """

        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as cli_service:
            if isinstance(snmp_parameters, SNMPV3Parameters):
                enable_snmp = self._enable_snmp_v3
            else:
                enable_snmp = self._enable_snmp_v2

            enable_snmp(cli_service=cli_service, snmp_parameters=snmp_parameters)

    def _wait_for_snmp_service(self, snmp_actions):
        """

        :param cloudshell.cumulus.linux.command_actions.snmp.BaseSnmpActions snmp_actions:
        :return:
        """
        timeout_time = datetime.now() + timedelta(seconds=self.SNMP_WAITING_TIMEOUT)

        while not snmp_actions.is_snmp_running():
            if datetime.now() > timeout_time:
                raise Exception("SNMP Service didn't started after 'Enable SNMP' command")

            self._logger.info("Waiting for SNMP service to start...")
            time.sleep(self.SNMP_WAITING_INTERVAL)

    def _enable_snmp_v2(self, cli_service, snmp_parameters):
        """

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        snmp_community = snmp_parameters.snmp_community

        if not snmp_community:
            raise Exception("SNMP community can not be empty")

        if isinstance(snmp_parameters, SNMPV2WriteParameters):
            raise Exception("Shell doesn't support SNMP v2 Read-write community")

        snmp_v2_actions = SnmpV2Actions(cli_service=cli_service, logger=self._logger)
        commit_actions = CommitActions(cli_service=cli_service, logger=self._logger)

        try:
            output = snmp_v2_actions.add_listening_address()
            output += snmp_v2_actions.create_view()
            output += snmp_v2_actions.enable_snmp(snmp_community=snmp_community)
            output += commit_actions.commit()
        except CommandExecutionException:
            self._logger.exception("Failed to Enable SNMPv2 on the device:")
            commit_actions.abort()
            raise

        self._wait_for_snmp_service(snmp_actions=snmp_v2_actions)
        return output

    def _enable_snmp_v3(self, cli_service, snmp_parameters):
        """

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        snmp_v3_actions = SnmpV3Actions(cli_service=cli_service, logger=self._logger)
        commit_actions = CommitActions(cli_service=cli_service, logger=self._logger)

        try:
            output = snmp_v3_actions.add_listening_address()
            output += snmp_v3_actions.create_view()
            output += snmp_v3_actions.enable_snmp(snmp_user=snmp_parameters.snmp_user,
                                                  snmp_password=snmp_parameters.snmp_password,
                                                  snmp_priv_key=snmp_parameters.snmp_private_key,
                                                  snmp_auth_proto=snmp_parameters.auth_protocol,
                                                  snmp_priv_proto=snmp_parameters.private_key_protocol)
            output += commit_actions.commit()
        except CommandExecutionException:
            commit_actions.abort()
            self._logger.exception("Failed to Enable SNMPv3 on the device:")
            raise

        self._wait_for_snmp_service(snmp_actions=snmp_v3_actions)
        return output
