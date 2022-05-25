import pytest

from cloudshell.cumulus.linux.connectivity.vlan_config_handler import (
    VlanQinqConfHandler,
)


@pytest.mark.parametrize(
    ("conf_text", "expected_conf_text"),
    (
        (  # empty config - creating a default bridge
            "",
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad""",
        ),
        (  # bridge is exists, do nothing
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad""",
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad""",
        ),
        (  # bridge exists but without vlan-aware setting
            """auto br_qinq
iface br_qinq""",
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad""",
        ),
        (  # vlan-aware set to "no" fix it
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware no
    bridge-vlan-protocol 802.1q""",
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad""",
        ),
    ),
)
def test_vlan_default_bridge(conf_text, expected_conf_text):
    conf = VlanQinqConfHandler(conf_text)

    conf.prepare_bridge()

    assert conf.text == expected_conf_text + "\n"
    assert conf.orig_text == conf_text


@pytest.mark.parametrize(
    ("conf_text", "map_port_vlan", "expected_conf_text"),
    (
        (  # creates first port and adds VLAN access to it
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad""",
            {"swp1": "14"},
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14
    bridge-ports swp1 vni-14

auto swp1
iface swp1
    bridge-access 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14""",
        ),
        (  # creates two more ports and adds VLANs to them
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14
    bridge-ports swp1 vni-14

auto swp1
iface swp1
    bridge-access 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14""",
            {"swp3": "16", "swp2": "15"},
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14 15 16
    bridge-ports swp1 swp2 swp3 vni-14 vni-15 vni-16

auto swp1
iface swp1
    bridge-access 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp3
iface swp3
    bridge-access 16

auto vni-16
iface vni-16
    bridge-access 16
    vxlan-id 16

auto swp2
iface swp2
    bridge-access 15

auto vni-15
iface vni-15
    bridge-access 15
    vxlan-id 15""",
        ),
    ),
)
def test_add_vlan_access(conf_text, map_port_vlan, expected_conf_text):
    conf = VlanQinqConfHandler(conf_text)

    for port_name, vlan_id in map_port_vlan.items():
        conf.add_access_vlan(port_name, vlan_id)

    assert conf.text == expected_conf_text + "\n"
    assert conf.orig_text == conf_text


@pytest.mark.parametrize(
    ("conf_text", "port_names", "expected_conf_text"),
    (
        (  # remove access VLAN from port
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14
    bridge-ports swp1 vni-14

auto swp1
iface swp1
    bridge-access 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14""",
            ["swp1"],
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad

auto swp1
iface swp1""",
        ),
        (  # remove 2 access VLANs from ports
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14 15 16
    bridge-ports swp1 swp3 swp2 vni-14 vni-15 vni-16

auto swp1
iface swp1
    bridge-access 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp3
iface swp3
    bridge-access 16

auto vni-16
iface vni-16
    bridge-access 16
    vxlan-id 16

auto swp2
iface swp2
    bridge-access 15

auto vni-15
iface vni-15
    bridge-access 15
    vxlan-id 15""",
            ["swp3", "swp2"],
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14
    bridge-ports swp1 vni-14

auto swp1
iface swp1
    bridge-access 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp3
iface swp3

auto swp2
iface swp2""",
        ),
        (  # remove access VLAN that uses by another port
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14 15
    bridge-ports swp1 swp3 swp2 vni-14 vni-15

auto swp1
iface swp1
    bridge-access 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp3
iface swp3
    bridge-access 14

auto swp2
iface swp2
    bridge-access 15

auto vni-15
iface vni-15
    bridge-access 15
    vxlan-id 15""",
            ["swp3"],
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14 15
    bridge-ports swp1 swp2 vni-14 vni-15

auto swp1
iface swp1
    bridge-access 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp3
iface swp3

auto swp2
iface swp2
    bridge-access 15

auto vni-15
iface vni-15
    bridge-access 15
    vxlan-id 15""",
        ),
        (  # remove all VLANs from the port
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14 15
    bridge-ports swp1 swp2 swp3 vni-14 vni-15

auto swp1
iface swp1
    bridge-access 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp3
iface swp3
    bridge-access 14

auto swp2
iface swp2
    bridge-access 15

auto vni-15
iface vni-15
    bridge-access 15
    vxlan-id 15""",
            ["swp3"],
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14 15
    bridge-ports swp1 swp2 vni-14 vni-15

auto swp1
iface swp1
    bridge-access 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp3
iface swp3

auto swp2
iface swp2
    bridge-access 15

auto vni-15
iface vni-15
    bridge-access 15
    vxlan-id 15""",
        ),
        (  # remove VLAN on the port without VLAN
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14
    bridge-ports swp1 vni-14

auto swp1
iface swp1
    bridge-access 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp2
iface swp2""",
            ["swp2"],
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14
    bridge-ports swp1 vni-14

auto swp1
iface swp1
    bridge-access 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp2
iface swp2""",
        ),
    ),
)
def test_remove_vlan_access(conf_text, port_names, expected_conf_text):
    conf = VlanQinqConfHandler(conf_text)

    for port_name in port_names:
        conf.remove_access_vlan(port_name)

    assert conf.text == expected_conf_text + "\n"
    assert conf.orig_text == conf_text


@pytest.mark.parametrize(
    ("conf_text", "map_port_vlan", "expected_conf_text"),
    (
        (  # creates first port and adds VLAN trunk to it
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad""",
            {"swp1": "13"},
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 13
    bridge-ports swp1 vni-13

auto swp1
iface swp1
    bridge-vids 13

auto vni-13
iface vni-13
    bridge-access 13
    vxlan-id 13""",
        ),
        (  # creates two more ports and adds VLANs to them
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 13
    bridge-ports swp1 vni-13

auto swp1
iface swp1
    bridge-vids 13

auto vni-13
iface vni-13
    bridge-access 13
    vxlan-id 13""",
            {"swp3": "16", "swp2": "15"},
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 13 15 16
    bridge-ports swp1 swp2 swp3 vni-13 vni-15 vni-16

auto swp1
iface swp1
    bridge-vids 13

auto vni-13
iface vni-13
    bridge-access 13
    vxlan-id 13

auto swp3
iface swp3
    bridge-vids 16

auto vni-16
iface vni-16
    bridge-access 16
    vxlan-id 16

auto swp2
iface swp2
    bridge-vids 15

auto vni-15
iface vni-15
    bridge-access 15
    vxlan-id 15""",
        ),
    ),
)
def test_add_vlan_trunk(conf_text, map_port_vlan, expected_conf_text):
    conf = VlanQinqConfHandler(conf_text)

    for port_name, vlan_id in map_port_vlan.items():
        conf.add_trunk_vlan(port_name, [vlan_id])

    assert conf.text == expected_conf_text + "\n"
    assert conf.orig_text == conf_text


@pytest.mark.parametrize(
    ("conf_text", "port_names", "expected_conf_text"),
    (
        (  # remove trunk VLAN from port
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14
    bridge-ports swp1 vni-14

auto swp1
iface swp1
    bridge-vids 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14""",
            ["swp1"],
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad

auto swp1
iface swp1""",
        ),
        (  # remove 2 trunk VLANs from ports
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14 15 16
    bridge-ports swp1 swp3 swp2 vni-14 vni-15 vni-16

auto swp1
iface swp1
    bridge-vids 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp3
iface swp3
    bridge-vids 16

auto vni-16
iface vni-16
    bridge-access 16
    vxlan-id 16

auto swp2
iface swp2
    bridge-vids 15

auto vni-15
iface vni-15
    bridge-access 15
    vxlan-id 15""",
            ["swp3", "swp2"],
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14
    bridge-ports swp1 vni-14

auto swp1
iface swp1
    bridge-vids 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp3
iface swp3

auto swp2
iface swp2""",
        ),
        (  # remove trunk VLAN that uses by another port
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14 15
    bridge-ports swp1 swp3 swp2 vni-14 vni-15

auto swp1
iface swp1
    bridge-vids 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp3
iface swp3
    bridge-vids 14

auto swp2
iface swp2
    bridge-vids 15

auto vni-15
iface vni-15
    bridge-access 15
    vxlan-id 15""",
            ["swp3"],
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14 15
    bridge-ports swp1 swp2 vni-14 vni-15

auto swp1
iface swp1
    bridge-vids 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp3
iface swp3

auto swp2
iface swp2
    bridge-vids 15

auto vni-15
iface vni-15
    bridge-access 15
    vxlan-id 15""",
        ),
        (  # remove all VLANs from the port
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14 15
    bridge-ports swp1 swp2 swp3 vni-14 vni-15

auto swp1
iface swp1
    bridge-vids 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp3
iface swp3
    bridge-vids 14

auto swp2
iface swp2
    bridge-vids 15

auto vni-15
iface vni-15
    bridge-access 15
    vxlan-id 15""",
            ["swp2"],
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14
    bridge-ports swp1 swp3 vni-14

auto swp1
iface swp1
    bridge-vids 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp3
iface swp3
    bridge-vids 14

auto swp2
iface swp2""",
        ),
        (  # remove VLAN on the port without VLAN
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14
    bridge-ports swp1 vni-14

auto swp1
iface swp1
    bridge-vids 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp2
iface swp2""",
            ["swp2"],
            """auto br_qinq
iface br_qinq
    bridge-vlan-aware yes
    bridge-vlan-protocol 802.1ad
    bridge-vids 14
    bridge-ports swp1 vni-14

auto swp1
iface swp1
    bridge-vids 14

auto vni-14
iface vni-14
    bridge-access 14
    vxlan-id 14

auto swp2
iface swp2""",
        ),
    ),
)
def test_remove_vlan_trunk(conf_text, port_names, expected_conf_text):
    conf = VlanQinqConfHandler(conf_text)

    for port_name in port_names:
        conf.remove_trunk_vlan(port_name)

    assert conf.text == expected_conf_text + "\n"
    assert conf.orig_text == conf_text
