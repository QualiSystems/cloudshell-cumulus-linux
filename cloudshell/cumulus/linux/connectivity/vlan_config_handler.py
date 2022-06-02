from __future__ import annotations

from cloudshell.cumulus.linux.connectivity.iface_config_handler import (
    IfaceConfig,
    IfaceSection,
)


def get_vni_name(vlan_id: str) -> str:
    return f"vni-{vlan_id}"


class VlanConfHandler:
    DEFAULT_BRIDGE_NAME = "br_default"
    QINQ_BRIDGE_NAME = "br_qinq"

    def __init__(self, orig_text: str):
        self.conf = IfaceConfig(orig_text)

    @property
    def text(self) -> str:
        return f"{self.conf.text}\n"

    @property
    def orig_text(self) -> str:
        return self.conf.orig_text

    def prepare_bridge(self, qinq: bool) -> None:
        bridge_name = self.QINQ_BRIDGE_NAME if qinq else self.DEFAULT_BRIDGE_NAME
        bridge = self.conf.get_iface(bridge_name)
        if not bridge:
            bridge = IfaceSection.create_bridge(bridge_name, self.conf)
        bridge.add_vlan_aware(True)
        if qinq:
            bridge.add_vlan_protocol_qinq()

    def remove_vlan(self, port_name: str) -> None:
        default_bridge = self.conf.get_iface(self.DEFAULT_BRIDGE_NAME)
        qinq_bridge = self.conf.get_iface(self.QINQ_BRIDGE_NAME)
        iface = self.conf.get_iface(port_name)
        vlans_to_remove = set()

        if iface:
            vlan_id = iface.get_access_vlan()
            if vlan_id:
                iface.remove_access_vlan()
                vlans_to_remove.add(vlan_id)
            vlans_to_remove.update(iface.get_trunk_vlans())
            iface.remove_trunk_vlan()

        for vlan_id in vlans_to_remove:
            if not self.conf.is_vlan_used(vlan_id, exclude_bridges=True):
                if default_bridge:
                    default_bridge.remove_trunk_vlan(vlan_id)

                vni_name = get_vni_name(vlan_id)
                self.conf.remove_iface(vni_name)
                if qinq_bridge:
                    qinq_bridge.remove_port(vni_name)
                    qinq_bridge.remove_trunk_vlan(vlan_id)

        if default_bridge:
            default_bridge.remove_port(port_name)
        if qinq_bridge:
            qinq_bridge.remove_port(port_name)

    def add_access_vlan(self, port_name: str, vlan_id: str, qinq: bool) -> None:
        iface = self.conf.get_or_create_iface(port_name)
        iface.set_access_vlan(vlan_id)

        bridge_name = self.QINQ_BRIDGE_NAME if qinq else self.DEFAULT_BRIDGE_NAME
        bridge = self.conf.get_iface(bridge_name)
        bridge.add_trunk_vlans([vlan_id])
        bridge.add_port(port_name)

        if qinq:
            vni_name = self._add_vni(vlan_id)
            bridge.add_port(vni_name)

    def add_trunk_vlan(self, port_name: str, vlans: list[str], qinq: bool) -> None:
        iface = self.conf.get_or_create_iface(port_name)
        iface.add_trunk_vlans(vlans)

        bridge_name = self.QINQ_BRIDGE_NAME if qinq else self.DEFAULT_BRIDGE_NAME
        bridge = self.conf.get_iface(bridge_name)
        bridge.add_trunk_vlans(vlans)
        bridge.add_port(port_name)

        if qinq:
            vni_name = self._add_vni(vlans[0])  # QinQ only supports one VLAN
            bridge.add_port(vni_name)

    def _add_vni(self, vlan_id: str) -> str:
        vni_name = get_vni_name(vlan_id)
        vni = self.conf.get_or_create_iface(vni_name)
        vni.set_access_vlan(vlan_id)
        vni.set_vxlan(vlan_id)
        return vni_name
