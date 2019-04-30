from cloudshell.cumulus.linux.flows.load_firmware import CumulusLinuxLoadFirmwareFlow
from cloudshell.devices.runners.firmware_runner import FirmwareRunner


class CumulusLinuxFirmwareRunner(FirmwareRunner):
    @property
    def load_firmware_flow(self):
        return CumulusLinuxLoadFirmwareFlow(cli_handler=self.cli_handler, logger=self._logger)
