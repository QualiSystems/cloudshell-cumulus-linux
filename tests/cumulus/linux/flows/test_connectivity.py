from __future__ import annotations

import json

import pytest

from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectionModeEnum,
    ConnectivityActionModel,
)
from cloudshell.shell.flows.connectivity.parse_request_service import (
    ParseConnectivityRequestService,
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


def test_set_vlan_failed(cli_emu: CliEmu, logger, resource_conf, create_action_request):
    orig_conf = "auto br_default\niface br_default"
    new_conf = """auto br_default
iface br_default

auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 10
    bridge-ports swp2 vni-10

auto swp2
iface swp2
    bridge-access 10

auto vni-10
iface vni-10
    bridge-access 10
    vxlan-id 10"""
    request = create_action_request(
        set_vlan=True,
        vlan_id="10",
        mode=ConnectionModeEnum.ACCESS,
        qnq=True,
        port_name="swp2",
    )
    request = {"driverRequest": {"actions": [request]}}
    ios = [
        *ENTER_ROOT_MODE,
        Input("cat /etc/network/interfaces && echo"),
        Output(orig_conf, Prompt.ROOT),
        Input(f'printf "{orig_conf}\n" > /etc/network/interfaces'),
        Output("", Prompt.ROOT),
        Input("ifreload -a"),
        Output("", Prompt.ROOT),
        Input(""),  # start set VLAN, receive the session and check prompt
        Output("", Prompt.ROOT),
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

    flow = CumulusConnectivityFlow(
        ParseConnectivityRequestService(
            is_vlan_range_supported=True, is_multi_vlan_supported=True
        ),
        logger,
        resource_conf,
        test_cli,
    )
    resp = flow.apply_connectivity(json.dumps(request))
    resp = json.loads(resp)
    assert resp
    assert len(resp["driverResponse"]["actionResults"]) == 1
    result = resp["driverResponse"]["actionResults"][0]
    assert result["success"] is False
    emsg = "version of Cumulus doesn't support 2 VLAN aware bridges"
    assert emsg in result["errorMessage"]

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


def test_not_worked(cli_emu: CliEmu, logger, resource_conf, create_action_request):
    action = create_action_request(
        set_vlan=True,
        vlan_id="500",
        mode=ConnectionModeEnum.ACCESS,
        qnq=True,
        port_name="swp3",
    )
    request = json.dumps({"driverRequest": {"actions": [action]}})
    orig_conf = """# Auto-generated by NVUE!
# Any local modifications will prevent NVUE from re-generating this file.
# md5sum: 5d90fa0e4d8af28dcae1b4832e137f29
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*.intf

auto lo
iface lo inet loopback

auto mgmt
iface mgmt
    address 127.0.0.1/8
    address ::1/128
    vrf-table auto

auto eth0
iface eth0 inet dhcp
    ip-forward off
    ip6-forward off
    vrf mgmt

auto swp2
iface swp2

auto swp3
iface swp3

auto br_default
iface br_default
    bridge-ports swp3
    hwaddress 00:50:56:a8:9c:e5
    bridge-vlan-aware yes
    bridge-vids 1
    bridge-pvid 1

auto swp1
iface swp1

auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad

"""
    conf_after_remove_vlan = """# Auto-generated by NVUE!
# Any local modifications will prevent NVUE from re-generating this file.
# md5sum: 5d90fa0e4d8af28dcae1b4832e137f29
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*.intf

auto lo
iface lo inet loopback

auto mgmt
iface mgmt
    address 127.0.0.1/8
    address ::1/128
    vrf-table auto

auto eth0
iface eth0 inet dhcp
    ip-forward off
    ip6-forward off
    vrf mgmt

auto swp2
iface swp2

auto swp3
iface swp3

auto br_default
iface br_default
    hwaddress 00:50:56:a8:9c:e5
    bridge-vlan-aware yes
    bridge-vids 1
    bridge-pvid 1

auto swp1
iface swp1

auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
"""
    conf_after_set_vlan = """# Auto-generated by NVUE!
# Any local modifications will prevent NVUE from re-generating this file.
# md5sum: 5d90fa0e4d8af28dcae1b4832e137f29
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*.intf

auto lo
iface lo inet loopback

auto mgmt
iface mgmt
    address 127.0.0.1/8
    address ::1/128
    vrf-table auto

auto eth0
iface eth0 inet dhcp
    ip-forward off
    ip6-forward off
    vrf mgmt

auto swp2
iface swp2

auto swp3
iface swp3
    bridge-access 500

auto br_default
iface br_default
    hwaddress 00:50:56:a8:9c:e5
    bridge-vlan-aware yes
    bridge-vids 1
    bridge-pvid 1

auto swp1
iface swp1

auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 500
    bridge-ports swp3 vni-500

auto vni-500
iface vni-500
    bridge-access 500
    vxlan-id 500
"""
    ios = [
        *ENTER_ROOT_MODE,
        Input("cat /etc/network/interfaces && echo"),
        Output(orig_conf, Prompt.ROOT),
        Input(f'printf "{conf_after_remove_vlan}" > /etc/network/interfaces'),
        Output("", Prompt.ROOT),
        Input("ifreload -a"),
        Output("", Prompt.ROOT),
        Input(""),  # get session from pool is set VLAN
        Output("", Prompt.ROOT),
        Input("cat /etc/network/interfaces && echo"),
        Output(conf_after_remove_vlan, Prompt.ROOT),
        Input(f'printf "{conf_after_set_vlan}" > /etc/network/interfaces'),
        Output("", Prompt.ROOT),
        Input("ifreload -a"),
        Output("", Prompt.ROOT),
    ]
    test_cli = cli_emu.create_cli(ios)

    service = ParseConnectivityRequestService(True, True)
    flow = CumulusConnectivityFlow(service, logger, resource_conf, test_cli)
    flow.apply_connectivity(request)
    cli_emu.validate_all_ios_executed()
