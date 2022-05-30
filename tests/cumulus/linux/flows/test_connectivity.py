from __future__ import annotations

import pytest

from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectionModeEnum,
    ConnectivityActionModel,
)

from cloudshell.cumulus.linux.command_templates import (
    CommandError,
    NotSupports2VlanAwareBridges,
)
from cloudshell.cumulus.linux.flows.connectivity_flow import CumulusConnectivityFlow

from tests.cumulus.linux.conftest import ENTER_ROOT_MODE, CliEmu, Input, Output, Prompt


@pytest.fixture()
def create_action_request():
    def creator(
        set_vlan: bool,
        vlan_id: str = "10",
        mode: ConnectionModeEnum = ConnectionModeEnum.ACCESS,
        qnq: bool = False,
        port_name: str = "swp2",
    ):
        return {
            "connectionId": "96582265-2728-43aa-bc97-cefb2457ca44",
            "connectionParams": {
                "vlanId": vlan_id,
                "mode": mode.value,
                "vlanServiceAttributes": [
                    {
                        "attributeName": "QnQ",
                        "attributeValue": str(qnq),
                        "type": "vlanServiceAttribute",
                    },
                    {
                        "attributeName": "CTag",
                        "attributeValue": "",
                        "type": "vlanServiceAttribute",
                    },
                ],
                "type": "setVlanParameter",
            },
            "connectorAttributes": [],
            "actionTarget": {
                "fullName": f"cumulus/{port_name}",
                "fullAddress": "full address",
                "type": "actionTarget",
            },
            "customActionAttributes": [],
            "actionId": "96582265-2728-43aa-bc97-cefb2457ca44_0900c4b5-0f90-42e3-b495",
            "type": "setVlan" if set_vlan else "removeVlan",
        }

    return creator


@pytest.fixture()
def create_vlan_action(create_action_request):
    def creator(
        set_vlan: bool,
        vlan_id: str = "10",
        mode: ConnectionModeEnum = ConnectionModeEnum.ACCESS,
        qnq: bool = False,
        port_name: str = "swp2",
    ):
        request = create_action_request(set_vlan, vlan_id, mode, qnq, port_name)
        return ConnectivityActionModel.parse_obj(request)

    return creator


@pytest.mark.parametrize(
    ("vlan_id", "mode", "qnq", "port_name", "orig_conf", "new_conf"),
    (
        (
            "10",
            ConnectionModeEnum.ACCESS,
            False,
            "swp2",
            "",
            """auto br_default
iface br_default
    bridge-vlan-aware yes
    bridge-vids 10
    bridge-ports swp2

auto swp2
iface swp2
    bridge-access 10""",
        ),
        (
            "14-16",
            ConnectionModeEnum.TRUNK,
            False,
            "swp3",
            "",
            """auto br_default
iface br_default
    bridge-vlan-aware yes
    bridge-vids 14 15 16
    bridge-ports swp3

auto swp3
iface swp3
    bridge-vids 14 15 16""",
        ),
        (
            "14",
            ConnectionModeEnum.ACCESS,
            True,
            "swp3",
            "auto br_default\niface br_default\n",
            """auto br_default
iface br_default

auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14
    bridge-ports swp3 vni-14

auto swp3
iface swp3
    bridge-access 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14""",
        ),
    ),
)
def test_set_vlan(
    cli_emu: CliEmu,
    logger,
    resource_conf,
    create_vlan_action,
    vlan_id,
    mode,
    qnq,
    port_name,
    orig_conf,
    new_conf,
):
    action = create_vlan_action(
        set_vlan=True, vlan_id=vlan_id, mode=mode, qnq=qnq, port_name=port_name
    )
    ios = [
        *ENTER_ROOT_MODE,
        Input("cat /etc/network/interfaces && echo"),
        Output(orig_conf, Prompt.ROOT),
        Input(f'printf "{new_conf}\n" > /etc/network/interfaces'),
        Output("", Prompt.ROOT),
        Input("ifreload -a"),
        Output("", Prompt.ROOT),
    ]
    test_cli = cli_emu.create_cli(ios)

    flow = CumulusConnectivityFlow(None, logger, resource_conf, test_cli)
    result = flow._set_vlan(action)
    assert result.success
    cli_emu.validate_all_ios_executed()


def test_set_vlan_failed_to_accept_new_conf(
    cli_emu: CliEmu, logger, resource_conf, create_vlan_action
):
    orig_conf = "auto br_default\niface br_default"
    new_conf = """auto br_default
iface br_default
    bridge-vlan-aware yes
    bridge-vids 10
    bridge-ports swp2

auto swp2
iface swp2
    bridge-access 10"""
    action = create_vlan_action(
        set_vlan=True,
        vlan_id="10",
        mode=ConnectionModeEnum.ACCESS,
        qnq=False,
        port_name="swp2",
    )
    ios = [
        *ENTER_ROOT_MODE,
        Input("cat /etc/network/interfaces && echo"),
        Output(orig_conf, Prompt.ROOT),
        Input(f'printf "{new_conf}\n" > /etc/network/interfaces'),
        Output("", Prompt.ROOT),
        Input("ifreload -a"),
        Output(
            "Only one object with attribute 'bridge-vlan-aware yes' allowed",
            Prompt.ROOT,
        ),
        Input(f'printf "{orig_conf}" > /etc/network/interfaces'),
        Output("", Prompt.ROOT),
        Input("ifreload -a"),
        Output("", Prompt.ROOT),
    ]
    test_cli = cli_emu.create_cli(ios)

    flow = CumulusConnectivityFlow(None, logger, resource_conf, test_cli)
    with pytest.raises(NotSupports2VlanAwareBridges):
        flow._set_vlan(action)
    cli_emu.validate_all_ios_executed()


@pytest.mark.parametrize(
    ("vlan_id", "mode", "qnq", "port_name", "orig_conf", "new_conf"),
    (
        (
            "10",
            ConnectionModeEnum.ACCESS,
            False,
            "swp2",
            """auto br_default
iface br_default
    bridge-vlan-aware yes
    bridge-vids 10
    bridge-ports swp2

auto swp2
iface swp2
    bridge-access 10""",
            """auto br_default
iface br_default
    bridge-vlan-aware yes

auto swp2
iface swp2""",
        ),
        (
            "14-16",
            ConnectionModeEnum.TRUNK,
            False,
            "swp3",
            """auto br_default
iface br_default
    bridge-vlan-aware yes
    bridge-vids 14 15 16
    bridge-ports swp3

auto swp3
iface swp3
    bridge-vids 14 15 16""",
            """auto br_default
iface br_default
    bridge-vlan-aware yes

auto swp3
iface swp3""",
        ),
        (
            "14",
            ConnectionModeEnum.ACCESS,
            True,
            "swp3",
            """auto br_default
iface br_default

auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14
    bridge-ports swp3 vni-14

auto swp3
iface swp3
    bridge-access 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14""",
            """auto br_default
iface br_default

auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad

auto swp3
iface swp3""",
        ),
    ),
)
def test_remove_vlan(
    cli_emu: CliEmu,
    logger,
    resource_conf,
    create_vlan_action,
    vlan_id,
    mode,
    qnq,
    port_name,
    orig_conf,
    new_conf,
):
    action = create_vlan_action(
        set_vlan=False, vlan_id=vlan_id, mode=mode, qnq=qnq, port_name=port_name
    )
    ios = [
        *ENTER_ROOT_MODE,
        Input("cat /etc/network/interfaces && echo"),
        Output(orig_conf, Prompt.ROOT),
        Input(f'printf "{new_conf}\n" > /etc/network/interfaces'),
        Output("", Prompt.ROOT),
        Input("ifreload -a"),
        Output("", Prompt.ROOT),
    ]
    test_cli = cli_emu.create_cli(ios)

    flow = CumulusConnectivityFlow(None, logger, resource_conf, test_cli)
    result = flow._remove_vlan(action)
    assert result.success
    cli_emu.validate_all_ios_executed()


def test_remove_vlan_failed_to_accept_new_conf(
    cli_emu: CliEmu, logger, resource_conf, create_vlan_action
):
    orig_conf = """auto br_default
iface br_default
    bridge-vlan-aware yes
    bridge-vids 10
    bridge-ports swp2

auto swp2
iface swp2
    bridge-access 10"""
    new_conf = """auto br_default
iface br_default
    bridge-vlan-aware yes

auto swp2
iface swp2"""
    action = create_vlan_action(
        set_vlan=False,
        vlan_id="10",
        mode=ConnectionModeEnum.ACCESS,
        qnq=False,
        port_name="swp2",
    )
    ios = [
        *ENTER_ROOT_MODE,
        Input("cat /etc/network/interfaces && echo"),
        Output(orig_conf, Prompt.ROOT),
        Input(f'printf "{new_conf}\n" > /etc/network/interfaces'),
        Output("", Prompt.ROOT),
        Input("ifreload -a"),
        Output("error:", Prompt.ROOT),
        Input(f'printf "{orig_conf}" > /etc/network/interfaces'),
        Output("", Prompt.ROOT),
        Input("ifreload -a"),
        Output("", Prompt.ROOT),
    ]
    test_cli = cli_emu.create_cli(ios)

    flow = CumulusConnectivityFlow(None, logger, resource_conf, test_cli)
    with pytest.raises(CommandError):
        flow._remove_vlan(action)
    cli_emu.validate_all_ios_executed()
