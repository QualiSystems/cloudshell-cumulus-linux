from cloudshell.cumulus.linux.flows.add_vlan import CumulusLinuxAddVlanFlow
from cloudshell.cumulus.linux.flows.remove_vlan import CumulusLinuxRemoveVlanFlow
from cloudshell.devices.runners.connectivity_runner import ConnectivityRunner


class CumulusLinuxConnectivityRunner(ConnectivityRunner):
    @property
    def add_vlan_flow(self):
        return CumulusLinuxAddVlanFlow(self.cli_handler, self._logger)

    @property
    def remove_vlan_flow(self):
        return CumulusLinuxRemoveVlanFlow(self.cli_handler, self._logger)
