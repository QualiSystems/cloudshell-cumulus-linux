from cloudshell.cumulus.linux.flows.shutdown import CumulusLinuxShutdownFlow
from cloudshell.devices.runners.state_runner import StateRunner


class CumulusLinuxStateRunner(StateRunner):
    @property
    def shutdown_flow(self):
        """

        :return:
        """
        return CumulusLinuxShutdownFlow(cli_handler=self.cli_handler, logger=self._logger)

    def shutdown(self):
        """

        :return:
        """
        return self.shutdown_flow.execute_flow()
