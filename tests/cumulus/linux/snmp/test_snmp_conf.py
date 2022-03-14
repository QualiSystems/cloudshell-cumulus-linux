import pytest as pytest

from cloudshell.cumulus.linux.snmp.snmp_conf_handler import SnmpConfigHandler


@pytest.mark.parametrize(
    ("conf_text", "ip", "vrf", "expected_conf_text"),
    (
        ("", "192.168.1.1", None, "agentAddress 192.168.1.1"),
        ("", "192.168.1.1", "mgt", "agentAddress 192.168.1.1@mgt"),
        (
            "agentaddress 192.168.2.1",
            "192.168.1.1",
            "mgt",
            "agentaddress 192.168.2.1\nagentAddress 192.168.1.1@mgt",
        ),
        (
            "agentaddress 192.168.1.1@mgt",
            "192.168.1.1",
            "mgt",
            "agentaddress 192.168.1.1@mgt",
        ),
        (
            "agentaddress 192.168.1.1",
            "192.168.1.1",
            "mgt",
            "agentaddress 192.168.1.1\nagentAddress 192.168.1.1@mgt",
        ),
        (
            "agentaddress 192.168.1.1",
            "192.168.1.1",
            "",
            "agentaddress 192.168.1.1",
        ),
    ),
)
def test_add_server_ip(conf_text, ip, vrf, expected_conf_text):
    conf = SnmpConfigHandler(conf_text)

    conf.add_server_ip(ip, vrf)

    assert conf.get_new_conf() == f"{expected_conf_text}\n"


@pytest.mark.parametrize(
    ("conf_text", "ip", "vrf", "expected_conf_text"),
    (
        ("", "192.168.1.1", "mgt", ""),
        ("agentAddress 192.168.1.1", "192.168.1.1", "", ""),
        ("agentAddress 192.168.1.1", "192.168.1.1", "mgt", "agentAddress 192.168.1.1"),
        ("agentAddress 192.168.1.1@mgt", "192.168.1.1", "mgt", ""),
        (
            "agentAddress localhost 192.168.1.1",
            "192.168.1.1",
            None,
            "agentAddress localhost 192.168.1.1",
        ),
    ),
)
def test_remove_server_ip(conf_text, ip, vrf, expected_conf_text):
    conf = SnmpConfigHandler(conf_text)

    conf.remove_server_ip(ip, vrf)

    assert conf.get_new_conf() == f"{expected_conf_text}\n"
