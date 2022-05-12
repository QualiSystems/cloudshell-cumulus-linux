from __future__ import annotations

import re
from typing import Generator

import attr
from typing_extensions import Literal

from cloudshell.snmp.snmp_parameters import SNMPV3Parameters

from cloudshell.cumulus.linux.const import DEFAULT_VIEW_NAME


class AttrName:
    server_address = "agentAddress"
    view = "view"
    ro_community = "rocommunity"
    rw_community = "rwcommunity"
    create_user = "createuser"
    rw_user = "rwuser"


def _get_priv_proto_str(priv_proto: str) -> str:
    if priv_proto in (SNMPV3Parameters.PRIV_DES, SNMPV3Parameters.PRIV_3DES):
        priv_proto_str = "DES"
    else:
        priv_proto_str = "AES"
    return priv_proto_str


@attr.s(auto_attribs=True, slots=True, frozen=True)
class SnmpConfigHandler:
    orig_text: str
    _lines: list[str] = attr.ib(default=[], init=False)

    def __attrs_post_init__(self):
        self._lines[:] = self.orig_text.splitlines()

    def get_new_conf(self) -> str:
        return "\n".join(self._lines) + "\n"

    def get(self, name: str) -> Generator[str, None, None]:
        name = name.lower()
        for line in self._lines:
            try:
                key, value_str = line.split(" ", 1)
            except ValueError:
                continue
            if key.lower() == name:
                yield value_str

    def add_to_conf(self, name: str, value: str):
        new_line = f"{name} {value}"
        self._lines.append(new_line)

    def remove_from_conf(self, name: str, value: str):
        line = f"{name} {value}"
        try:
            self._lines.remove(line)
        except ValueError:
            pass  # config doesn't have such line

    def get_server_ips(self) -> Generator[str, None, None]:
        for value_str in self.get(AttrName.server_address):
            yield from map(str.strip, value_str.split(","))

    @staticmethod
    def _get_server_ip_value_str(ip: str, vrf: str | None) -> str:
        value = ip
        if vrf:
            value = f"{value}@{vrf}"
        return value

    def add_server_ip(self, ip: str, vrf: str | None = None) -> None:
        expected_str = self._get_server_ip_value_str(ip, vrf)
        for server_ip in self.get_server_ips():
            if re.search(rf"(^|:){expected_str}($|)", server_ip):
                break
        else:
            self.add_to_conf(AttrName.server_address, expected_str)

    def remove_server_ip(self, ip: str, vrf: str | None = None) -> None:
        value = self._get_server_ip_value_str(ip, vrf)
        self.remove_from_conf(AttrName.server_address, value)

    @staticmethod
    def _get_view_value_str(name: str) -> str:
        return f"{name} included .1"

    def create_view(self, name: str = DEFAULT_VIEW_NAME):
        for value in self.get(AttrName.view):
            if value.split(" ", 1)[0] == name:
                break
        else:
            self.add_to_conf(AttrName.view, self._get_view_value_str(name))

    def remove_view(self, name: str = DEFAULT_VIEW_NAME):
        value = self._get_view_value_str(name)
        self.remove_from_conf(AttrName.view, value)

    @staticmethod
    def _get_community_value_str(community: str, view: str) -> str:
        return f"{community} default -V {view}"

    def add_ro_community(self, community: str, view_name: str = DEFAULT_VIEW_NAME):
        self._add_community("ro", community, view_name)

    def add_rw_community(self, community: str, view_name: str = DEFAULT_VIEW_NAME):
        self._add_community("rw", community, view_name)

    def _add_community(
        self, type_: Literal["rw", "ro"], community: str, view_name: str
    ) -> None:
        expected_val = self._get_community_value_str(community, view_name)
        attr_name = AttrName.rw_community if type_ == "rw" else AttrName.ro_community
        for value in self.get(attr_name):
            if value == expected_val:
                break
        else:
            self.add_to_conf(attr_name, expected_val)

    def remove_ro_community(self, community: str, view_name: str = DEFAULT_VIEW_NAME):
        self._remove_community("ro", community, view_name)

    def remove_rw_community(self, community: str, view_name: str = DEFAULT_VIEW_NAME):
        self._remove_community("rw", community, view_name)

    def _remove_community(
        self, type_: Literal["rw", "ro"], community: str, view_name: str
    ) -> None:
        value = self._get_community_value_str(community, view_name)
        attr_name = AttrName.rw_community if type_ == "rw" else AttrName.ro_community
        self.remove_from_conf(attr_name, value)

    @staticmethod
    def _get_create_user_value_str(
        username: str, auth_proto: str, password: str, priv_proto: str, priv_key: str
    ) -> str:
        value = f"{username}"
        if auth_proto != SNMPV3Parameters.AUTH_NO_AUTH:
            value += f" {auth_proto} {password}"
            if priv_proto != SNMPV3Parameters.PRIV_NO_PRIV:
                priv_proto_str = _get_priv_proto_str(priv_proto)
                value += f" {priv_proto_str} {priv_key}"
        return value

    @staticmethod
    def _get_rwuser_value_str(
        username: str, auth_proto: str, priv_proto: str, view_name: str
    ) -> str:
        if auth_proto == SNMPV3Parameters.AUTH_NO_AUTH:
            auth = "noauth"
        else:
            if priv_proto == SNMPV3Parameters.PRIV_NO_PRIV:
                auth = "auth"
            else:
                auth = "priv"
        return f"{username} {auth} -V {view_name}"

    def create_user(
        self,
        username: str,
        auth_proto: str,
        password: str,
        priv_proto: str,
        priv_key: str,
        view_name: str = DEFAULT_VIEW_NAME,
    ):
        create_user_value = self._get_create_user_value_str(
            username, auth_proto, password, priv_proto, priv_key
        )
        for value in self.get(AttrName.create_user):
            if value == create_user_value:
                break
        else:
            self.add_to_conf(AttrName.create_user, create_user_value)

        rw_user_value = self._get_rwuser_value_str(
            username, auth_proto, priv_proto, view_name
        )
        for value in self.get(AttrName.rw_user):
            if value == rw_user_value:
                break
        else:
            self.add_to_conf(AttrName.rw_user, rw_user_value)

    def remove_user(self, username: str):
        create_user_pattern = re.compile(rf"^{username}(\s|$)")
        rw_user_pattern = re.compile(rf"^{username}\s")
        values_to_remove = []
        for value in self.get(AttrName.create_user):
            if create_user_pattern.search(value):
                values_to_remove.append(value)
        for value in values_to_remove:
            self.remove_from_conf(AttrName.create_user, value)

        values_to_remove = []
        for value in self.get(AttrName.rw_user):
            if rw_user_pattern.search(value):
                values_to_remove.append(value)
        for value in values_to_remove:
            self.remove_from_conf(AttrName.rw_user, value)
