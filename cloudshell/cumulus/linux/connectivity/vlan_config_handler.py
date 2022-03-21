from __future__ import annotations

from abc import abstractmethod
from typing import ClassVar, Iterable

from cloudshell.cumulus.linux.connectivity.iface_config_handler import (
    IfaceConfig,
    IfaceSection,
)


def get_vni_name(vlan_id: str) -> str:
    return f"vni-{vlan_id}"


class AbstractVlanConfHandler:
    def __init__(self, orig_text: str):
        self.conf = IfaceConfig(orig_text)

    @property
    def text(self) -> str:
        return self.conf.text

    @property
    def orig_text(self) -> str:
        return self.conf.orig_text

    @abstractmethod
    def prepare_bridge(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_access_vlan(self, port_name: str, vlan_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_access_vlan(self, port_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_trunk_vlan(self, port_name: str, vlans: Iterable[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_trunk_vlan(self, port_name: str) -> None:
        raise NotImplementedError


class VlanConfHandler(AbstractVlanConfHandler):
    BRIDGE_NAME: ClassVar[str] = "br_default"

    def prepare_bridge(self) -> None:
        bridge = self.conf.get_iface(self.BRIDGE_NAME)
        if not bridge:
            bridge = IfaceSection.create_bridge(self.BRIDGE_NAME, self.conf)
        bridge.add_vlan_aware(True)

    def add_access_vlan(self, port_name: str, vlan_id: str) -> None:
        iface = self.conf.get_iface(port_name)
        if not iface:
            iface = IfaceSection.create_iface(port_name, self.conf)
        iface.set_access_vlan(vlan_id)
        iface.remove_trunk_vlan()

        bridge = self.conf.get_iface(self.BRIDGE_NAME)
        bridge.add_trunk_vlans([vlan_id])
        bridge.add_port(port_name)

    def remove_access_vlan(self, port_name: str) -> None:
        bridge = self.conf.get_iface(self.BRIDGE_NAME)
        iface = self.conf.get_iface(port_name)
        if iface:
            vlan_id = iface.get_access_vlan()
            if vlan_id:
                iface.remove_access_vlan()
                if not self.conf.is_vlan_used(vlan_id, exclude_bridges=True):
                    bridge.remove_trunk_vlan(vlan_id)
            bridge.remove_port(port_name)

    def add_trunk_vlan(self, port_name: str, vlans: Iterable[str]) -> None:
        iface = self.conf.get_iface(port_name)
        if not iface:
            iface = IfaceSection.create_iface(port_name, self.conf)
        iface.add_trunk_vlans(vlans)
        iface.remove_access_vlan()

        bridge = self.conf.get_iface(self.BRIDGE_NAME)
        bridge.add_trunk_vlans(vlans)
        bridge.add_port(port_name)

    def remove_trunk_vlan(self, port_name: str) -> None:
        bridge = self.conf.get_iface(self.BRIDGE_NAME)
        iface = self.conf.get_iface(port_name)
        if iface:
            vlans = iface.get_trunk_vlans()
            for vlan_id in vlans:
                iface.remove_trunk_vlan(vlan_id)
                if not self.conf.is_vlan_used(vlan_id, exclude_bridges=True):
                    bridge.remove_trunk_vlan(vlan_id)
            bridge.remove_port(port_name)


class VlanQinqConfHandler(AbstractVlanConfHandler):
    BRIDGE_NAME: ClassVar[str] = "br_qinq"

    def prepare_bridge(self) -> None:
        bridge = self.conf.get_iface(self.BRIDGE_NAME)
        if not bridge:
            bridge = IfaceSection.create_bridge(self.BRIDGE_NAME, self.conf)
        bridge.add_vlan_aware(True)
        bridge.add_vlan_protocol_qinq()

    def add_access_vlan(self, port_name: str, vlan_id: str) -> None:
        iface = self.conf.get_iface(port_name)
        if not iface:
            iface = IfaceSection.create_iface(port_name, self.conf)
        iface.set_access_vlan(vlan_id)
        iface.remove_trunk_vlan()

        vni_name = get_vni_name(vlan_id)
        vni = self.conf.get_iface(vni_name)
        if not vni:
            vni = IfaceSection.create_iface(vni_name, self.conf)
        vni.set_access_vlan(vlan_id)
        vni.remove_trunk_vlan()
        vni.set_vxlan(vlan_id)

        bridge = self.conf.get_iface(self.BRIDGE_NAME)
        bridge.add_trunk_vlans([vlan_id])
        bridge.add_port(port_name)
        bridge.add_port(vni_name)

    def remove_access_vlan(self, port_name: str) -> None:
        bridge = self.conf.get_iface(self.BRIDGE_NAME)
        iface = self.conf.get_iface(port_name)
        if iface:
            vlan_id = iface.get_access_vlan()
            if vlan_id:
                iface.remove_access_vlan()
                if not self.conf.is_vlan_used(vlan_id, exclude_bridges=True):
                    vni_name = get_vni_name(vlan_id)
                    self.conf.remove_iface(vni_name)
                    bridge.remove_port(vni_name)
                    bridge.remove_trunk_vlan(vlan_id)
            bridge.remove_port(port_name)

    def add_trunk_vlan(self, port_name: str, vlans: Iterable[str]) -> None:
        vlan_id = next(iter(vlans))
        iface = self.conf.get_iface(port_name)
        if not iface:
            iface = IfaceSection.create_iface(port_name, self.conf)
        iface.add_trunk_vlans([vlan_id])
        iface.remove_access_vlan()

        vni_name = get_vni_name(vlan_id)
        vni = self.conf.get_iface(vni_name)
        if not vni:
            vni = IfaceSection.create_iface(vni_name, self.conf)
        vni.set_access_vlan(vlan_id)
        vni.remove_trunk_vlan()
        vni.set_vxlan(vlan_id)

        bridge = self.conf.get_iface(self.BRIDGE_NAME)
        bridge.add_trunk_vlans([vlan_id])
        bridge.add_port(port_name)
        bridge.add_port(vni_name)

    def remove_trunk_vlan(self, port_name: str) -> None:
        bridge = self.conf.get_iface(self.BRIDGE_NAME)
        iface = self.conf.get_iface(port_name)
        if iface:
            vlans = iface.get_trunk_vlans()
            for vlan_id in vlans:
                iface.remove_trunk_vlan(vlan_id)
                if not self.conf.is_vlan_used(vlan_id, exclude_bridges=True):
                    vni_name = get_vni_name(vlan_id)
                    self.conf.remove_iface(vni_name)
                    bridge.remove_port(vni_name)
                    bridge.remove_trunk_vlan(vlan_id)
            bridge.remove_port(port_name)
