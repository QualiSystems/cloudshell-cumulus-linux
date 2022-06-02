from __future__ import annotations

import re
from typing import ClassVar, Iterable

import attr

from cloudshell.cumulus.linux.utils.cached_property import cached_property


class SettingName:
    VLAN_AWARE = "bridge-vlan-aware"
    VLAN_PROTOCOL = "bridge-vlan-protocol"
    ACCESS_VLAN = "bridge-access"
    TRUNK_VLAN = "bridge-vids"
    VXLAN_ID = "vxlan-id"
    PORTS = "bridge-ports"


@attr.s(auto_attribs=True, slots=True, repr=False)
class Setting:
    priv_text: str
    iface: IfaceSection
    _text: str = attr.ib(default="", init=False)

    @staticmethod
    def _get_setting_line(name: str, values: Iterable[str]) -> str:
        return f"    {name} {' '.join(values)}"

    @classmethod
    def create(cls, name: str, values: Iterable[str], iface: IfaceSection) -> Setting:
        line = cls._get_setting_line(name, values)
        setting = Setting(line, iface)
        iface.add_setting(setting)
        return setting

    def __attrs_post_init__(self):
        self._text = self.priv_text

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.text})"

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        self.iface.update_setting(self)
        self.priv_text = self.text

    @property
    def _text_without_indent(self):
        return self.text.lstrip(" ")

    @property
    def name(self) -> str:
        return self._text_without_indent.split(" ", 1)[0]

    @property
    def values(self) -> tuple[str]:
        return tuple(self._text_without_indent.split(" ")[1:])

    @values.setter
    def values(self, vals: Iterable[str]) -> None:
        self.text = self._get_setting_line(self.name, vals)
        self.iface.update_setting(self)


@attr.s(auto_attribs=True, slots=True, repr=False)
class IfaceSection:
    priv_text: str
    iface_config: IfaceConfig
    _text: str = attr.ib(default="", init=False)

    def __attrs_post_init__(self):
        self._text = self.priv_text

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.text})"

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        self.iface_config.update_iface(self)
        self.priv_text = self.text

    @classmethod
    def create_iface(cls, name: str, iface_config: IfaceConfig) -> IfaceSection:
        text = f"auto {name}\niface {name}"
        iface = cls(text, iface_config)
        iface_config.add_iface(iface)
        return iface

    @classmethod
    def create_bridge(cls, name: str, iface_config: IfaceConfig) -> IfaceSection:
        return cls.create_iface(name, iface_config)

    @cached_property
    def name(self) -> str:
        return self.text.splitlines()[0].split(" ", 1)[-1]

    # CRUD settings
    def get_setting(self, name: str) -> Setting | None:
        match = re.search(rf"^\s{{4}}{name}\s.+$", self.text, re.MULTILINE)
        if not match:
            return None
        else:
            return Setting(match.group(), self)

    def add_setting(self, setting: Setting) -> None:
        self.text = f"{self.text}\n{setting.text}"

    def update_setting(self, setting: Setting) -> None:
        self.text = self.text.replace(setting.priv_text, setting.text)

    def remove_setting(self, name: str) -> None:
        setting = self.get_setting(name)
        if setting:
            self.text = self.text.replace(f"\n{setting.priv_text}", "")

    # bridge settings
    def add_vlan_aware(self, vlan_aware: bool) -> None:
        value = "yes" if vlan_aware else "no"
        setting = self.get_setting(SettingName.VLAN_AWARE)
        if setting:
            setting.values = [value]
        else:
            Setting.create(SettingName.VLAN_AWARE, [value], self)

    def add_vlan_protocol_qinq(self):
        setting = self.get_setting(SettingName.VLAN_PROTOCOL)
        value = "802.1ad"
        if setting:
            setting.values = [value]
        else:
            Setting.create(SettingName.VLAN_PROTOCOL, [value], self)

    # VLAN access
    def set_access_vlan(self, vlan_id: str) -> None:
        setting = self.get_setting(SettingName.ACCESS_VLAN)
        if setting:
            setting.values = [vlan_id]
        else:
            Setting.create(SettingName.ACCESS_VLAN, [vlan_id], self)

    def get_access_vlan(self) -> str | None:
        setting = self.get_setting(SettingName.ACCESS_VLAN)
        if setting:
            return setting.values[0]

    def remove_access_vlan(self):
        self.remove_setting(SettingName.ACCESS_VLAN)

    # VLAN trunk
    def add_trunk_vlans(self, vlans: Iterable[str]) -> None:
        setting = self.get_setting(SettingName.TRUNK_VLAN)
        if setting:
            try:
                vlans = sorted({*setting.values, *vlans}, key=int)
            except ValueError:
                # can't sort, VLANs are not integers
                vlans = list({*setting.values, *vlans})
            setting.values = vlans
        else:
            Setting.create(SettingName.TRUNK_VLAN, sorted(vlans), self)

    def remove_trunk_vlan(self, vlan_id: str | None = None) -> None:
        if not vlan_id:
            self.remove_setting(SettingName.TRUNK_VLAN)
        else:
            setting = self.get_setting(SettingName.TRUNK_VLAN)
            if setting:
                vlans = setting.values
                if vlan_id in vlans:
                    vlans = list(vlans)
                    vlans.remove(vlan_id)

                    if vlans:
                        setting.values = vlans
                    else:
                        self.remove_setting(SettingName.TRUNK_VLAN)

    def get_trunk_vlans(self) -> tuple[str]:
        setting = self.get_setting(SettingName.TRUNK_VLAN)
        return getattr(setting, "values", [])

    # VXLAN
    def set_vxlan(self, vlan_id: str) -> None:
        setting = self.get_setting(SettingName.VXLAN_ID)
        if setting:
            setting.values = [vlan_id]
        else:
            Setting.create(SettingName.VXLAN_ID, [vlan_id], self)

    # bridge ports
    def add_port(self, name: str) -> None:
        setting = self.get_setting(SettingName.PORTS)
        if setting:
            ports = sorted({*setting.values, name})
            setting.values = ports
        else:
            Setting.create(SettingName.PORTS, [name], self)

    def remove_port(self, name: str) -> None:
        setting = self.get_setting(SettingName.PORTS)
        if setting:
            ports = setting.values
            if name in ports:
                ports = list(ports)
                ports.remove(name)

                if ports:
                    setting.values = ports
                else:
                    self.remove_setting(SettingName.PORTS)


@attr.s(auto_attribs=True, slots=True, repr=False)
class IfaceConfig:
    """Adds/removes VLANs to/from ports via editing /etc/network/interface file."""

    BR_DEFAULT: ClassVar[str] = "br_default"
    BR_QINQ: ClassVar[str] = "br_qinq"
    orig_text: str
    text: str = attr.ib(default="", init=False)

    def __attrs_post_init__(self):
        self.text = self.orig_text

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.text})"

    def get_iface(self, iface_name: str) -> IfaceSection | None:
        pattern = re.compile(rf"auto {iface_name}\niface {iface_name}(\n\s{{4}}.+)*")
        match = pattern.search(self.text)
        if match:
            return IfaceSection(match.group(), self)

    def get_or_create_iface(self, iface_name: str) -> IfaceSection:
        iface = self.get_iface(iface_name)
        if not iface:
            iface = IfaceSection.create_iface(iface_name, self)
        return iface

    def update_iface(self, iface: IfaceSection) -> None:
        self.text = self.text.replace(iface.priv_text, iface.text)

    def add_iface(self, iface: IfaceSection) -> None:
        self.text = f"{self.text}\n\n{iface.text}".strip("\n")

    def remove_iface(self, iface_name: str) -> None:
        iface = self.get_iface(iface_name)
        if iface:
            self.text = re.sub(rf"\n*{re.escape(iface.priv_text)}", "", self.text)

    def is_vlan_used(self, vlan_id: str, exclude_bridges: bool) -> bool:
        exclude_vin = rf"(?!vni-{vlan_id})"
        iface_pattern = rf"{exclude_vin}\S+"
        if exclude_bridges:
            iface_pattern = rf"(?!({self.BR_DEFAULT}|{self.BR_QINQ})){iface_pattern}"

        pattern = re.compile(
            rf"auto {iface_pattern}\n"
            rf"iface {iface_pattern}"
            rf"(\n\s{{4}}.+)*"
            rf"\n\s{{4}}(bridge-access {vlan_id}|bridge-vids(\s\d+)*\s{vlan_id})"
        )
        return bool(pattern.search(self.text))
