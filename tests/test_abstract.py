"""Тесты абстрактного класса на примере Huawei."""

from collections import deque
from pathlib import Path
from textwrap import dedent

import pytest

from conf_tree import ConfTree, ConfTreeParser, HuaweiCT, TaggingRulesFile, Vendor


@pytest.fixture(scope="function")
def huawei_manual_config() -> dict[str, ConfTree]:
    # sflow collector 1 ip 100.64.0.1 vpn-instance MGMT
    # #
    # storm suppression statistics enable
    # #
    # ip vpn-instance MGMT
    #  ipv4-family
    #   route-distinguisher 192.168.0.1:123
    # #
    # ip vpn-instance LAN
    #  ipv4-family
    #   route-distinguisher 192.168.0.1:123
    #   vpn-target 123:123 export-extcommunity evpn
    #   vpn-target 123:123 import-extcommunity evpn
    #  vxlan vni 123
    # #
    # interface gi0/0/0
    #  description test
    #  ip address 1.1.1.1 255.255.255.252
    # #
    # interface gi0/0/1
    #  ip address 1.1.1.1 255.255.255.252
    #  load-interval 30
    # #
    # ntp-service authentication-keyid 1 authentication-mode md5 cipher secret_password
    # #
    # radius-server template RADIUS_TEMPLATE
    #  radius-server shared-key cipher secret_password
    #  radius-server algorithm loading-share

    root = HuaweiCT()
    sflow = HuaweiCT("sflow collector 1 ip 100.64.0.1 vpn-instance MGMT", root)
    storm = HuaweiCT("storm suppression statistics enable", root)
    mgmt = HuaweiCT("ip vpn-instance MGMT", root)
    ipv4_af_mgmt = HuaweiCT(" ipv4-family", mgmt)
    rd_mgmt = HuaweiCT("  route-distinguisher 192.168.0.1:123", ipv4_af_mgmt)
    lan = HuaweiCT("ip vpn-instance LAN", root)
    ipv4_af_lan = HuaweiCT(" ipv4-family", lan)
    rd_lan = HuaweiCT("  route-distinguisher 192.168.0.1:123", ipv4_af_lan)
    rt_export = HuaweiCT("  vpn-target 123:123 export-extcommunity evpn", ipv4_af_lan)
    rt_import = HuaweiCT("  vpn-target 123:123 import-extcommunity evpn", ipv4_af_lan)
    vxlan = HuaweiCT(" vxlan vni 123", lan)
    intf_000 = HuaweiCT("interface gi0/0/0", root)
    description_000 = HuaweiCT(" description test", intf_000)
    ip_000 = HuaweiCT(" ip address 1.1.1.1 255.255.255.252", intf_000)
    intf_001 = HuaweiCT("interface gi0/0/1", root)
    ip_001 = HuaweiCT(" ip address 1.1.1.1 255.255.255.252", intf_001)
    load_interval_001 = HuaweiCT(" load-interval 30", intf_001)
    ntp = HuaweiCT("ntp-service authentication-keyid 1 authentication-mode md5 cipher secret_password", root)
    radius = HuaweiCT("radius-server template RADIUS_TEMPLATE", root)
    radius_key = HuaweiCT(" radius-server shared-key cipher secret_password", radius)
    radius_algorithm = HuaweiCT(" radius-server algorithm loading-share", radius)

    return locals()


def test_basic_creation(huawei_manual_config: dict[str, ConfTree]) -> None:
    root = huawei_manual_config
    assert str(root["root"]) == "root"
    assert root["sflow"].parent == root["root"]
    assert root["sflow"].line in root["root"].children
    assert len(root["root"].children) == 8
    assert len(root["lan"].children) == 2
    assert len(root["ipv4_af_lan"].children) == 3
    assert str(root["rt_export"]) == "vpn-target 123:123 export-extcommunity evpn"
    assert root["lan"].parent == root["mgmt"].parent


def test_eq(huawei_manual_config: dict[str, ConfTree]) -> None:
    # interface gi0/0/0
    #  description test
    #  ip address 1.1.1.1 255.255.255.252
    # radius-server template RADIUS_TEMPLATE
    root = huawei_manual_config
    other_root = HuaweiCT()
    other_intf_000 = HuaweiCT("interface gi0/0/0", other_root)
    other_radius = HuaweiCT("radius-server template RADIUS_TEMPLATE", other_root)
    assert root["intf_000"] != other_intf_000
    other_ip_000 = HuaweiCT(" ip address 1.1.1.1 255.255.255.252", other_intf_000)
    _ = HuaweiCT(" description test", other_intf_000)
    assert root["root"] != other_root
    assert root["intf_000"] == other_intf_000
    assert root["ip_000"] == other_ip_000
    assert root["intf_001"] != other_intf_000
    assert root["ip_001"] != other_ip_000
    assert root["radius"] != other_radius
    assert HuaweiCT() != NotImplemented

    other_root = HuaweiCT()
    other_intf_000 = HuaweiCT("interface gi0/0/0", other_root)
    _ = HuaweiCT(" ip address 1.1.1.2 255.255.255.252", other_intf_000)
    _ = HuaweiCT(" description test", other_intf_000)
    assert root["intf_000"] != other_intf_000


def test_repr(huawei_manual_config: dict[str, ConfTree]) -> None:
    root = huawei_manual_config
    assert repr(root["root"]) == f"({id(root['root'])}) 'root'"


def test_config(huawei_manual_config: dict[str, ConfTree]) -> None:
    config = dedent(
        """
        sflow collector 1 ip 100.64.0.1 vpn-instance MGMT
        #
        storm suppression statistics enable
        #
        ip vpn-instance MGMT
         ipv4-family
          route-distinguisher 192.168.0.1:123
        #
        ip vpn-instance LAN
         ipv4-family
          route-distinguisher 192.168.0.1:123
          vpn-target 123:123 export-extcommunity evpn
          vpn-target 123:123 import-extcommunity evpn
         vxlan vni 123
        #
        interface gi0/0/0
         description test
         ip address 1.1.1.1 255.255.255.252
        #
        interface gi0/0/1
         ip address 1.1.1.1 255.255.255.252
         load-interval 30
        #
        ntp-service authentication-keyid 1 authentication-mode md5 cipher secret_password
        #
        radius-server template RADIUS_TEMPLATE
         radius-server shared-key cipher secret_password
         radius-server algorithm loading-share
        #
        """
    ).strip()
    root = huawei_manual_config["root"]
    assert root.config == config


def test_masked_config(huawei_manual_config: dict[str, ConfTree]) -> None:
    masked_config = dedent(
        f"""
        sflow collector 1 ip 100.64.0.1 vpn-instance MGMT
        #
        storm suppression statistics enable
        #
        ip vpn-instance MGMT
         ipv4-family
          route-distinguisher 192.168.0.1:123
        #
        ip vpn-instance LAN
         ipv4-family
          route-distinguisher 192.168.0.1:123
          vpn-target 123:123 export-extcommunity evpn
          vpn-target 123:123 import-extcommunity evpn
         vxlan vni 123
        #
        interface gi0/0/0
         description test
         ip address 1.1.1.1 255.255.255.252
        #
        interface gi0/0/1
         ip address 1.1.1.1 255.255.255.252
         load-interval 30
        #
        ntp-service authentication-keyid 1 authentication-mode md5 cipher {HuaweiCT.masking_string}
        #
        radius-server template RADIUS_TEMPLATE
         radius-server shared-key cipher {HuaweiCT.masking_string}
         radius-server algorithm loading-share
        #
        """
    ).strip()
    root = huawei_manual_config["root"]
    assert root.masked_config == masked_config


def test_patch(huawei_manual_config: dict[str, ConfTree]) -> None:
    patch = dedent(
        """
        sflow collector 1 ip 100.64.0.1 vpn-instance MGMT
        storm suppression statistics enable
        ip vpn-instance MGMT
        ipv4-family
        route-distinguisher 192.168.0.1:123
        quit
        quit
        ip vpn-instance LAN
        ipv4-family
        route-distinguisher 192.168.0.1:123
        vpn-target 123:123 export-extcommunity evpn
        vpn-target 123:123 import-extcommunity evpn
        quit
        vxlan vni 123
        quit
        interface gi0/0/0
        description test
        ip address 1.1.1.1 255.255.255.252
        quit
        interface gi0/0/1
        ip address 1.1.1.1 255.255.255.252
        load-interval 30
        quit
        ntp-service authentication-keyid 1 authentication-mode md5 cipher secret_password
        radius-server template RADIUS_TEMPLATE
        radius-server shared-key cipher secret_password
        radius-server algorithm loading-share
        quit
        """
    ).strip()
    root = huawei_manual_config["root"]
    assert root.patch == patch


def test_masked_patch(huawei_manual_config: dict[str, ConfTree]) -> None:
    masked_patch = dedent(
        f"""
        sflow collector 1 ip 100.64.0.1 vpn-instance MGMT
        storm suppression statistics enable
        ip vpn-instance MGMT
        ipv4-family
        route-distinguisher 192.168.0.1:123
        quit
        quit
        ip vpn-instance LAN
        ipv4-family
        route-distinguisher 192.168.0.1:123
        vpn-target 123:123 export-extcommunity evpn
        vpn-target 123:123 import-extcommunity evpn
        quit
        vxlan vni 123
        quit
        interface gi0/0/0
        description test
        ip address 1.1.1.1 255.255.255.252
        quit
        interface gi0/0/1
        ip address 1.1.1.1 255.255.255.252
        load-interval 30
        quit
        ntp-service authentication-keyid 1 authentication-mode md5 cipher {HuaweiCT.masking_string}
        radius-server template RADIUS_TEMPLATE
        radius-server shared-key cipher {HuaweiCT.masking_string}
        radius-server algorithm loading-share
        quit
        """
    ).strip()
    root = huawei_manual_config["root"]
    assert root.masked_patch == masked_patch


def test_copy(huawei_manual_config: dict[str, ConfTree]) -> None:
    def get_nodes_list(root: ConfTree) -> list[ConfTree]:
        stack = deque(root.children.values())
        nodes = []
        while len(stack) > 0:
            node = stack.popleft()
            nodes.append(node)
            if len(node.children) != 0:
                stack.extendleft(list(node.children.values())[::-1])
        return nodes

    root = HuaweiCT()
    lan = HuaweiCT("ip vpn-instance LAN", root)
    af = HuaweiCT(" ipv4-family", lan)
    _ = HuaweiCT("  route-distinguisher 192.168.0.1:123", af)
    _ = HuaweiCT("  vpn-target 123:123 export-extcommunity evpn", af)
    _ = HuaweiCT("  vpn-target 123:123 import-extcommunity evpn", af)

    copy1 = root.copy()
    copy2 = root.copy()
    copy3 = huawei_manual_config["root"].children["ip vpn-instance LAN"].children["ipv4-family"].copy()
    assert root == copy1
    assert root == copy2
    assert root == copy3

    root_nodes = get_nodes_list(root)
    copy1_nodes = get_nodes_list(copy1)
    copy2_nodes = get_nodes_list(copy2)
    copy3_nodes = get_nodes_list(copy3)

    assert len(root_nodes) == len(copy1_nodes)
    assert len(root_nodes) == len(copy2_nodes)
    assert len(root_nodes) == len(copy3_nodes)

    for indx in range(len(root_nodes)):
        assert root_nodes[indx] == copy1_nodes[indx]
        assert root_nodes[indx] == copy2_nodes[indx]
        assert root_nodes[indx] == copy3_nodes[indx]
        assert id(root_nodes[indx]) != id(copy1_nodes[indx])
        assert id(root_nodes[indx]) != id(copy2_nodes[indx])
        assert id(root_nodes[indx]) != id(copy3_nodes[indx])
        assert id(copy1_nodes[indx]) != id(copy2_nodes[indx])
        assert id(copy1_nodes[indx]) != id(copy3_nodes[indx])
        assert id(copy2_nodes[indx]) != id(copy3_nodes[indx])


def test_merge() -> None:
    config = dedent(
        """
        ip vpn-instance LAN
         ipv4-family
          route-distinguisher 192.168.0.1:123
          vpn-target 123:123 export-extcommunity evpn
          vpn-target 123:123 import-extcommunity evpn
         vxlan vni 123
        #
        """
    ).strip()

    root1 = HuaweiCT()
    lan = HuaweiCT("ip vpn-instance LAN", root1)
    af = HuaweiCT(" ipv4-family", lan)
    _ = HuaweiCT("  route-distinguisher 192.168.0.1:123", af)
    _ = HuaweiCT("  vpn-target 123:123 export-extcommunity evpn", af)
    _ = HuaweiCT("  vpn-target 123:123 import-extcommunity evpn", af)

    root2 = HuaweiCT()
    lan = HuaweiCT("ip vpn-instance LAN", root2)
    _ = HuaweiCT(" vxlan vni 123", lan)
    root1.merge(root2)
    assert root1.config == config
    vxlan1 = root1.children["ip vpn-instance LAN"].children["vxlan vni 123"]
    vxlan2 = root2.children["ip vpn-instance LAN"].children["vxlan vni 123"]
    assert id(vxlan1) != id(vxlan2)

    config = dedent(
        """
        interface gi0/0/0
         ip address 1.1.1.1 255.255.255.252
         description test
         undo shutdown
        #
        """
    ).strip()
    root1 = HuaweiCT()
    intf = HuaweiCT("interface gi0/0/0", root1)
    _ = HuaweiCT(" ip address 1.1.1.1 255.255.255.252", intf)
    _ = HuaweiCT(" description test", intf)

    root2 = HuaweiCT()
    intf = HuaweiCT("interface gi0/0/0", root2)
    _ = HuaweiCT(" undo shutdown", intf)

    root1.merge(root2)
    assert root1.config == config


def test_delete(huawei_manual_config: dict[str, ConfTree]) -> None:
    config = dedent(
        """
        sflow collector 1 ip 100.64.0.1 vpn-instance MGMT
        #
        storm suppression statistics enable
        #
        ip vpn-instance LAN
         vxlan vni 123
        #
        interface gi0/0/0
         description test
         ip address 1.1.1.1 255.255.255.252
        #
        interface gi0/0/1
         ip address 1.1.1.1 255.255.255.252
         load-interval 30
        #
        ntp-service authentication-keyid 1 authentication-mode md5 cipher secret_password
        #
        radius-server template RADIUS_TEMPLATE
         radius-server shared-key cipher secret_password
         radius-server algorithm loading-share
        #
        """
    ).strip()
    root = huawei_manual_config["root"]
    node1 = root.children["ip vpn-instance MGMT"]
    node2 = root.children["ip vpn-instance LAN"].children["ipv4-family"]
    node1.delete()
    node2.delete()
    assert root.config == config


def test_rebuild(huawei_manual_config: dict[str, ConfTree]) -> None:
    mgmt = huawei_manual_config["mgmt"]
    if not isinstance(mgmt, ConfTree) or not isinstance(mgmt.parent, ConfTree):
        raise AssertionError
    mgmt.line = "ip vpn-instance MGMT_NEW_NAME"
    mgmt.parent.rebuild()
    assert mgmt.line in mgmt.parent.children

    root = huawei_manual_config["root"]
    rd = root.children["ip vpn-instance LAN"].children["ipv4-family"].children["route-distinguisher 192.168.0.1:123"]
    if not isinstance(rd, ConfTree) or not isinstance(rd.parent, ConfTree):
        raise AssertionError
    rd.line = "route-distinguisher 1.2.3.4:567"
    assert rd.line not in rd.parent.children.keys()
    root.rebuild(deep=True)
    assert rd.line in rd.parent.children.keys()


def test_mask_line(huawei_manual_config: dict[str, ConfTree]) -> None:
    nodes = [
        huawei_manual_config["ntp"],
        huawei_manual_config["radius"].children.get("radius-server shared-key cipher secret_password"),
    ]
    raw_lines = [
        "ntp-service authentication-keyid 1 authentication-mode md5 cipher secret_password",
        "radius-server shared-key cipher secret_password",
    ]
    masked_lines = [
        f"ntp-service authentication-keyid 1 authentication-mode md5 cipher {HuaweiCT.masking_string}",
        f"radius-server shared-key cipher {HuaweiCT.masking_string}",
    ]
    for node, raw, masked in zip(nodes, raw_lines, masked_lines):
        if not isinstance(node, ConfTree):
            raise AssertionError
        assert node.line == raw
        assert node.masked_line == masked


def test_nested_config(huawei_manual_config: dict[str, ConfTree]) -> None:
    config = dedent(
        """
        ip vpn-instance LAN
         ipv4-family
          route-distinguisher 192.168.0.1:123
        """
    ).strip()
    rd = huawei_manual_config["rd_lan"]
    assert rd.config == config


def test_nested_patch(huawei_manual_config: dict[str, ConfTree]) -> None:
    patch = dedent(
        """
        ip vpn-instance LAN
        ipv4-family
        route-distinguisher 192.168.0.1:123
        quit
        quit
        quit
        """
    ).strip()
    rd = huawei_manual_config["rd_lan"]
    assert rd.patch == patch


def test_exists_in(huawei_manual_config: dict[str, ConfTree]) -> None:
    uut = huawei_manual_config["radius"]
    root = HuaweiCT()
    radius = HuaweiCT("radius-server template RADIUS_TEMPLATE", root)
    key_1 = HuaweiCT(" radius-server shared-key cipher new_secret_password", radius)
    key_2 = HuaweiCT(" radius-server shared-key cipher secret_password", radius)
    key_3 = HuaweiCT(" radius-server shared-key", radius)

    assert key_1.exists_in(uut) == ""
    assert key_1.exists_in(uut, masked=False) == ""
    assert key_1.exists_in(uut, masked=True) == "radius-server shared-key cipher secret_password"

    assert key_2.exists_in(uut) == "radius-server shared-key cipher secret_password"
    assert key_2.exists_in(uut, masked=False) == "radius-server shared-key cipher secret_password"
    assert key_2.exists_in(uut, masked=True) == "radius-server shared-key cipher secret_password"

    assert key_3.exists_in(uut) == ""
    assert key_3.exists_in(uut, masked=False) == ""
    assert key_3.exists_in(uut, masked=True) == ""


def test_formal_config(huawei_manual_config: dict[str, ConfTree]) -> None:
    formal_config = dedent(
        """
        sflow collector 1 ip 100.64.0.1 vpn-instance MGMT
        storm suppression statistics enable
        ip vpn-instance MGMT / ipv4-family / route-distinguisher 192.168.0.1:123
        ip vpn-instance LAN / ipv4-family / route-distinguisher 192.168.0.1:123
        ip vpn-instance LAN / ipv4-family / vpn-target 123:123 export-extcommunity evpn
        ip vpn-instance LAN / ipv4-family / vpn-target 123:123 import-extcommunity evpn
        ip vpn-instance LAN / vxlan vni 123
        interface gi0/0/0 / description test
        interface gi0/0/0 / ip address 1.1.1.1 255.255.255.252
        interface gi0/0/1 / ip address 1.1.1.1 255.255.255.252
        interface gi0/0/1 / load-interval 30
        ntp-service authentication-keyid 1 authentication-mode md5 cipher secret_password
        radius-server template RADIUS_TEMPLATE / radius-server shared-key cipher secret_password
        radius-server template RADIUS_TEMPLATE / radius-server algorithm loading-share
        """
    ).strip()
    root = huawei_manual_config["root"]
    assert root.formal_config == formal_config

    interface_formal_config = dedent(
        """
        interface gi0/0/0 / description test
        interface gi0/0/0 / ip address 1.1.1.1 255.255.255.252
        """
    ).strip()
    intf = huawei_manual_config["intf_000"]
    assert intf.formal_config == interface_formal_config

    ip = huawei_manual_config["ip_000"]
    assert ip.formal_config == "interface gi0/0/0 / ip address 1.1.1.1 255.255.255.252"


def test_reorder() -> None:
    config = dedent(
        """
        bgp 64512
         ipv4-family vpn-instance LAN
          peer PEER_GROUP_1 route-policy RP_NAME_1_IN import
         ipv4-family unicast
          import-route direct route-policy RP_CONNECTED
         ipv4-family vpn-instance LAN
          peer PEER_GROUP_2 route-policy RP_NAME_2_IN import
        #
        route-policy RP_CONNECTED permit node 10
         if-match ip-prefix PL_LOOPBACK
        #
        route-policy RP_CONNECTED permit node 20
         if-match ip-prefix PL_CONNECTED
        #
        route-policy RP_NAME_1_IN permit node 10
         if-match ip-prefix PL_NAME_1
         apply community community-list CL_NAME_1 additive
        #
        ip ip-prefix PL_NAME_1 index 10 permit 1.2.3.0 24 greater-equal 32 less-equal 32
        #
        ip ip-prefix PL_NAME_1 index 20 permit 2.3.4.0 24
        """
    ).strip()
    original = dedent(
        """
        bgp 64512
         ipv4-family vpn-instance LAN
          peer PEER_GROUP_1 route-policy RP_NAME_1_IN import
          peer PEER_GROUP_2 route-policy RP_NAME_2_IN import
         ipv4-family unicast
          import-route direct route-policy RP_CONNECTED
        #
        route-policy RP_CONNECTED permit node 10
         if-match ip-prefix PL_LOOPBACK
        #
        route-policy RP_CONNECTED permit node 20
         if-match ip-prefix PL_CONNECTED
        #
        route-policy RP_NAME_1_IN permit node 10
         if-match ip-prefix PL_NAME_1
         apply community community-list CL_NAME_1 additive
        #
        ip ip-prefix PL_NAME_1 index 10 permit 1.2.3.0 24 greater-equal 32 less-equal 32
        #
        ip ip-prefix PL_NAME_1 index 20 permit 2.3.4.0 24
        #
        """
    ).strip()
    reordered_pl_rp_bgp = dedent(
        """
        ip ip-prefix PL_NAME_1 index 10 permit 1.2.3.0 24 greater-equal 32 less-equal 32
        #
        ip ip-prefix PL_NAME_1 index 20 permit 2.3.4.0 24
        #
        route-policy RP_CONNECTED permit node 10
         if-match ip-prefix PL_LOOPBACK
        #
        route-policy RP_CONNECTED permit node 20
         if-match ip-prefix PL_CONNECTED
        #
        route-policy RP_NAME_1_IN permit node 10
         if-match ip-prefix PL_NAME_1
         apply community community-list CL_NAME_1 additive
        #
        bgp 64512
         ipv4-family vpn-instance LAN
          peer PEER_GROUP_1 route-policy RP_NAME_1_IN import
          peer PEER_GROUP_2 route-policy RP_NAME_2_IN import
         ipv4-family unicast
          import-route direct route-policy RP_CONNECTED
        #
        """
    ).strip()
    reordered_rp_pl_bgp = dedent(
        """
        route-policy RP_CONNECTED permit node 10
         if-match ip-prefix PL_LOOPBACK
        #
        route-policy RP_CONNECTED permit node 20
         if-match ip-prefix PL_CONNECTED
        #
        route-policy RP_NAME_1_IN permit node 10
         if-match ip-prefix PL_NAME_1
         apply community community-list CL_NAME_1 additive
        #
        ip ip-prefix PL_NAME_1 index 10 permit 1.2.3.0 24 greater-equal 32 less-equal 32
        #
        ip ip-prefix PL_NAME_1 index 20 permit 2.3.4.0 24
        #
        bgp 64512
         ipv4-family vpn-instance LAN
          peer PEER_GROUP_1 route-policy RP_NAME_1_IN import
          peer PEER_GROUP_2 route-policy RP_NAME_2_IN import
         ipv4-family unicast
          import-route direct route-policy RP_CONNECTED
        #
        """
    ).strip()
    reordered_bgp_pl = dedent(
        """
        bgp 64512
         ipv4-family vpn-instance LAN
          peer PEER_GROUP_1 route-policy RP_NAME_1_IN import
          peer PEER_GROUP_2 route-policy RP_NAME_2_IN import
         ipv4-family unicast
          import-route direct route-policy RP_CONNECTED
        #
        ip ip-prefix PL_NAME_1 index 10 permit 1.2.3.0 24 greater-equal 32 less-equal 32
        #
        ip ip-prefix PL_NAME_1 index 20 permit 2.3.4.0 24
        #
        route-policy RP_CONNECTED permit node 10
         if-match ip-prefix PL_LOOPBACK
        #
        route-policy RP_CONNECTED permit node 20
         if-match ip-prefix PL_CONNECTED
        #
        route-policy RP_NAME_1_IN permit node 10
         if-match ip-prefix PL_NAME_1
         apply community community-list CL_NAME_1 additive
        #
        """
    ).strip()

    reordered_rp_pl_bgp_reversed = dedent(
        """
        bgp 64512
         ipv4-family vpn-instance LAN
          peer PEER_GROUP_1 route-policy RP_NAME_1_IN import
          peer PEER_GROUP_2 route-policy RP_NAME_2_IN import
         ipv4-family unicast
          import-route direct route-policy RP_CONNECTED
        #
        ip ip-prefix PL_NAME_1 index 10 permit 1.2.3.0 24 greater-equal 32 less-equal 32
        #
        ip ip-prefix PL_NAME_1 index 20 permit 2.3.4.0 24
        #
        route-policy RP_CONNECTED permit node 10
         if-match ip-prefix PL_LOOPBACK
        #
        route-policy RP_CONNECTED permit node 20
         if-match ip-prefix PL_CONNECTED
        #
        route-policy RP_NAME_1_IN permit node 10
         if-match ip-prefix PL_NAME_1
         apply community community-list CL_NAME_1 additive
        #
        """
    ).strip()

    reordered_bgp_pl_reversed = dedent(
        """
        ip ip-prefix PL_NAME_1 index 10 permit 1.2.3.0 24 greater-equal 32 less-equal 32
        #
        ip ip-prefix PL_NAME_1 index 20 permit 2.3.4.0 24
        #
        bgp 64512
         ipv4-family vpn-instance LAN
          peer PEER_GROUP_1 route-policy RP_NAME_1_IN import
          peer PEER_GROUP_2 route-policy RP_NAME_2_IN import
         ipv4-family unicast
          import-route direct route-policy RP_CONNECTED
        #
        route-policy RP_CONNECTED permit node 10
         if-match ip-prefix PL_LOOPBACK
        #
        route-policy RP_CONNECTED permit node 20
         if-match ip-prefix PL_CONNECTED
        #
        route-policy RP_NAME_1_IN permit node 10
         if-match ip-prefix PL_NAME_1
         apply community community-list CL_NAME_1 additive
        #
        """
    ).strip()

    parser = ConfTreeParser(Vendor.HUAWEI, TaggingRulesFile(Path(__file__).with_suffix(".yaml")))

    root = parser.parse(config)
    assert root.config == original

    root.reorder([])
    assert root.config == original

    root.reorder(["pl", "rp", "bgp"])
    assert root.config == reordered_pl_rp_bgp

    root.reorder(["rp", "pl", "bgp"])
    assert root.config == reordered_rp_pl_bgp

    root.reorder(["bgp", "pl"])
    assert root.config == reordered_bgp_pl

    root.reorder(["rp", "pl", "bgp"], reverse=True)
    assert root.config == reordered_rp_pl_bgp_reversed

    root.reorder(["bgp", "pl"], reverse=True)
    assert root.config == reordered_bgp_pl_reversed


def test_tag_copy() -> None:
    root = HuaweiCT()
    lan = HuaweiCT("level-1", root)
    af = HuaweiCT("level-2", lan, ["af", "vpn", "LAN"])
    rd = HuaweiCT("level-3", af, af.tags)

    root_uut = rd.copy()
    rd_uut = root_uut.children["level-1"].children["level-2"].children["level-3"]
    rd_uut.tags.append("copied")
    assert rd.tags == ["af", "vpn", "LAN"]
    assert rd_uut.tags == ["af", "vpn", "LAN", "copied"]


def test_subtract() -> None:
    config1 = dedent(
        """
        aaa authentication login default local group group
        aaa authentication login console local
        aaa authentication enable default none
        aaa accounting commands all default start-stop logging
        #
        aaa group server tacacs+ group
         server 10.1.0.5 vrf MGMT
         server 10.1.0.6 vrf MGMT
         server 10.1.0.4 vrf MGMT
         server 10.1.0.2 vrf MGMT
         server 10.1.0.3 vrf MGMT
        #
        """
    ).strip()
    config2 = dedent(
        """
        aaa authentication login console local
        aaa authentication enable default none
        aaa accounting commands all default start-stop logging
        #
        aaa group server tacacs+ group
         server 10.1.0.6 vrf MGMT
         server 10.1.0.5 vrf MGMT
         server 10.1.0.4 vrf MGMT
         server 10.1.0.3 vrf MGMT
        #
        """
    ).strip()
    config1_config2 = dedent(
        """
        aaa authentication login default local group group
        #
        aaa group server tacacs+ group
         server 10.1.0.2 vrf MGMT
        #
        """
    ).strip()
    config2_config1 = ""
    parser = ConfTreeParser(vendor=Vendor.HUAWEI)
    root1 = parser.parse(config1)
    root2 = parser.parse(config2)
    diff = root1.subtract(root2)
    assert diff.config == config1_config2

    diff = root2.subtract(root1)
    assert diff.config == config2_config1


def test_apply() -> None:
    current_config = dedent(
        """
        line 1
        line 2
        section 3
         sub-line 3.1
        line 3
        section 1
         sub-line 1.1
        line 10
        section 5
         sub-line 5.1
        line 11
        """
    ).strip()
    diff_config = dedent(
        """
        line 1
        line 2
        undo section 4
        section 1
         undo sub-line 1.1
         sub-line 1.2
        line 4
        undo section 3
        section 2
         sub-line 2.1
        line 10
        section 5
         undo sub-line 5.1
        """
    ).strip()
    target_config = dedent(
        """
        line 1
        #
        line 2
        #
        line 3
        #
        section 1
         sub-line 1.2
        #
        line 10
        #
        section 5
        #
        line 11
        #
        line 4
        #
        section 2
         sub-line 2.1
        #
        """
    ).strip()
    parser = ConfTreeParser(vendor=Vendor.HUAWEI)
    current = parser.parse(current_config)
    diff = parser.parse(diff_config)
    target = current.apply(diff)
    assert target.config == target_config
