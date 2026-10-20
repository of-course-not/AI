# -*- coding: utf-8 -*-
"""按实验报告的四张拓扑生成 4 个 Packet Tracer 8.2.2 工程文件（.pkt）。

设备型号严格照原图；原图中的 Cisco 2501 在 PT 8.2.2 里不存在，
用 2621XM + WIC-2T 替代（见 README-PKT.md）。
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pktbuild as B
import pktlib

OUT = os.path.join(os.path.dirname(HERE), "03-工程文件")
os.makedirs(OUT, exist_ok=True)
_UID = [0]


def uid():
    _UID[0] += 1
    return 700000000 + _UID[0] * 7919


# ------------------------------------------------------------------ 工具
def set_pc(block, ip, mask, gw):
    """给 PC 的第一个 PORT 写地址/掩码/网关。"""
    i = block.find("<PORT>")
    j = block.find("</PORT>", i) + len("</PORT>")
    seg = block[i:j]
    seg = re.sub(r"<POWER>[^<]*</POWER>", "<POWER>true</POWER>", seg, 1)
    seg = re.sub(r"<IP/>|<IP>[^<]*</IP>", "<IP>%s</IP>" % ip, seg, 1)
    seg = re.sub(r"<SUBNET/>|<SUBNET>[^<]*</SUBNET>", "<SUBNET>%s</SUBNET>" % mask, seg, 1)
    seg = re.sub(r"<PORT_GATEWAY/>|<PORT_GATEWAY>[^<]*</PORT_GATEWAY>",
                 "<PORT_GATEWAY>%s</PORT_GATEWAY>" % gw, seg, 1)
    mac = B._mac()
    seg = re.sub(r"<MACADDRESS>[^<]*</MACADDRESS>", "<MACADDRESS>%s</MACADDRESS>" % mac, seg, 1)
    seg = re.sub(r"<BIA>[^<]*</BIA>", "<BIA>%s</BIA>" % mac, seg, 1)
    return block[:i] + seg + block[j:]


def remac(block):
    """重写全部 MAC，避免多台同型号设备 MAC 冲突。"""
    def sub(m):
        return "<%s>%s</%s>" % (m.group(1), B._mac(), m.group(1))
    return re.sub(r"<(MACADDRESS|BIA)>[^<]*</\1>", sub, block)


def power_all(block, kind):
    cfg = {n: ("", "", True) for n in B.port_names(kind, block)}
    return B.set_ports(block, kind, cfg)


def router(kind, name, x, y, ports, run, clocks=()):
    b = B.donor_device(kind)
    if kind == "2621XM":
        b, _ = B.with_wic2t(b)
    b = remac(b)
    b = B.set_ports(b, kind, ports)
    if clocks:
        b = B.set_clock(b, kind, set(clocks))
    b = B.rename(b, name, x, y, uid())
    b = B.set_running(b, run)
    return b


def switch(kind, name, x, y, vlans, run):
    b = B.donor_device(kind)
    b = remac(b)
    b = power_all(b, kind)
    b = B.rename(b, name, x, y, uid())
    if vlans:
        b = B.set_vlans(b, vlans)
    b = B.set_running(b, run)
    return b


def pc(name, x, y, ip, mask, gw):
    b = B.donor_device("PC-PT")
    b = B.rename(b, name, x, y, uid())
    return set_pc(b, ip, mask, gw)


def save(fn, devices, links, notes):
    xml = B.build(devices, links, notes=notes)
    pktlib.save(os.path.join(OUT, fn), xml)
    print("saved %s  (%d devices, %d links, %d chars)"
          % (fn, len(devices), len(links), len(xml)))


# ================================================================== 实验一
def lab1():
    sw = switch("2960-24TT", "SW1", 300, 200, [(10, "VLAN10"), (20, "VLAN20")], [
        "!", "hostname SW1", "!",
        "vlan 10", " name VLAN10", "vlan 20", " name VLAN20", "!",
        "interface FastEthernet0/1", " switchport access vlan 10",
        " switchport mode access", "!",
        "interface FastEthernet0/2", " switchport access vlan 20",
        " switchport mode access", "!",
        "interface FastEthernet0/24", " switchport mode trunk", "!",
        "end"])

    r1 = router("1841", "R1", 540, 200, {
        "FastEthernet0/0": ("", "", True),
        "FastEthernet0/1": ("", "", False),
        "Serial0/0/0": ("192.168.90.129", "255.255.255.252", True),
        "Serial0/0/1": ("", "", False),
    }, [
        "!", "hostname R1", "!",
        "interface Loopback0", " ip address 192.168.90.200 255.255.255.255", "!",
        "interface FastEthernet0/0", " no ip address", " no shutdown", "!",
        "interface FastEthernet0/0.10", " encapsulation dot1Q 10",
        " ip address 192.168.90.1 255.255.255.192", "!",
        "interface FastEthernet0/0.20", " encapsulation dot1Q 20",
        " ip address 192.168.90.65 255.255.255.192", "!",
        "interface FastEthernet0/1", " no ip address", " shutdown", "!",
        "interface Serial0/0/0", " ip address 192.168.90.129 255.255.255.252",
        " clock rate 64000", " no shutdown", "!",
        "interface Serial0/0/1", " no ip address", " shutdown", "!",
        "ip route 192.168.90.132 255.255.255.252 192.168.90.130", "!",
        "enable secret cisco123", "!",
        "line vty 0 4", " password telnet123", " login", "!",
        "end"], clocks={"Serial0/0/0"})

    r2 = router("1841", "R2", 780, 200, {
        "FastEthernet0/0": ("192.168.90.133", "255.255.255.252", True),
        "FastEthernet0/1": ("", "", False),
        "Serial0/0/0": ("192.168.90.130", "255.255.255.252", True),
        "Serial0/0/1": ("", "", False),
    }, [
        "!", "hostname R2", "!",
        "interface FastEthernet0/0", " ip address 192.168.90.133 255.255.255.252",
        " no shutdown", "!",
        "interface FastEthernet0/1", " no ip address", " shutdown", "!",
        "interface Serial0/0/0", " ip address 192.168.90.130 255.255.255.252",
        " no shutdown", "!",
        "interface Serial0/0/1", " no ip address", " shutdown", "!",
        "ip route 192.168.90.0 255.255.255.192 192.168.90.129",
        "ip route 192.168.90.64 255.255.255.192 192.168.90.129", "!",
        "end"])

    pca = pc("PC-A", 180, 400, "192.168.90.10", "255.255.255.192", "192.168.90.1")
    pcb = pc("PC-B", 340, 400, "192.168.90.74", "255.255.255.192", "192.168.90.65")
    pcc = pc("PC-C", 780, 400, "192.168.90.134", "255.255.255.252", "192.168.90.133")

    links = [
        B.make_link(0, "FastEthernet0/1", 3, "FastEthernet0"),
        B.make_link(0, "FastEthernet0/2", 4, "FastEthernet0"),
        B.make_link(0, "FastEthernet0/24", 1, "FastEthernet0/0"),
        B.make_link(1, "Serial0/0/0", 2, "Serial0/0/0", kind="eSerial", dce=1),
        B.make_link(2, "FastEthernet0/0", 5, "FastEthernet0", cable="eCrossOver"),
    ]
    notes = [
        (40, 40, "实验一  路由器基本配置 + 单臂路由（自设计拓扑）\n"
                 "学号后两位 90，主网 192.168.90.0/24\n"
                 "PC-A 192.168.90.10/26 gw .1    PC-B 192.168.90.74/26 gw .65    "
                 "PC-C 192.168.90.134/30 gw .133"),
        (40, 520, "验证顺序：\n"
                  "1) R1# show ip route  —— 看直连路由（接口 up 且有地址才出现）\n"
                  "2) PC-A ping 192.168.90.74  -> TTL=127（经 R1 子接口，1 跳）\n"
                  "3) PC-A ping 192.168.90.134 -> TTL=126（经 R1、R2，2 跳）\n"
                  "4) PC-A: telnet 192.168.90.1  密码 telnet123，enable 密码 cisco123"),
    ]
    save("90-实验一-路由器基本配置与单臂路由.pkt", [sw, r1, r2, pca, pcb, pcc], links, notes)


# ================================================================== 实验二
def lab2():
    sw = switch("3560-24PS", "SW0", 260, 200, [(2, "vlan2"), (3, "vlan3")], [
        "!", "hostname SW0", "!",
        "ip routing", "!",
        "interface FastEthernet0/2", " switchport access vlan 2",
        " switchport mode access", "!",
        "interface FastEthernet0/3", " switchport access vlan 3",
        " switchport mode access", "!",
        "interface Vlan2", " ip address 192.168.90.1 255.255.255.192", "!",
        "interface Vlan3", " ip address 192.168.90.65 255.255.255.192", "!",
        "interface FastEthernet0/1", " no switchport",
        " ip address 192.168.90.129 255.255.255.252", "!",
        "ip route 192.168.90.132 255.255.255.252 192.168.90.130",
        "ip route 192.168.90.136 255.255.255.252 192.168.90.130",
        "ip route 192.168.90.140 255.255.255.252 192.168.90.130",
        "ip route 192.168.90.144 255.255.255.252 192.168.90.130",
        "ip route 192.168.90.148 255.255.255.252 192.168.90.130", "!",
        "end"])

    r0 = router("1841", "R0", 520, 200, {
        "FastEthernet0/0": ("192.168.90.130", "255.255.255.252", True),
        "FastEthernet0/1": ("192.168.90.133", "255.255.255.252", True),
        "Serial0/0/0": ("192.168.90.137", "255.255.255.252", True),
        "Serial0/0/1": ("", "", False),
    }, [
        "!", "hostname R0", "!",
        "interface FastEthernet0/0", " ip address 192.168.90.130 255.255.255.252",
        " no shutdown", "!",
        "interface FastEthernet0/1", " ip address 192.168.90.133 255.255.255.252",
        " no shutdown", "!",
        "interface Serial0/0/0", " ip address 192.168.90.137 255.255.255.252",
        " clock rate 64000", " no shutdown", "!",
        "interface Serial0/0/1", " no ip address", " shutdown", "!",
        "ip route 192.168.90.0 255.255.255.192 192.168.90.129",
        "ip route 192.168.90.64 255.255.255.192 192.168.90.129",
        "ip route 192.168.90.140 255.255.255.252 192.168.90.138",
        "ip route 192.168.90.144 255.255.255.252 192.168.90.138",
        "ip route 192.168.90.148 255.255.255.252 192.168.90.138", "!",
        "end"], clocks={"Serial0/0/0"})

    r1 = router("1841", "R1", 790, 200, {
        "FastEthernet0/0": ("192.168.90.141", "255.255.255.252", True),
        "FastEthernet0/1": ("", "", False),
        "Serial0/0/0": ("192.168.90.138", "255.255.255.252", True),
        "Serial0/0/1": ("192.168.90.145", "255.255.255.252", True),
    }, [
        "!", "hostname R1", "!",
        "interface Serial0/0/0", " ip address 192.168.90.138 255.255.255.252",
        " no shutdown", "!",
        "interface Serial0/0/1", " ip address 192.168.90.145 255.255.255.252",
        " clock rate 64000", " no shutdown", "!",
        "interface FastEthernet0/0", " ip address 192.168.90.141 255.255.255.252",
        " no shutdown", "!",
        "interface FastEthernet0/1", " no ip address", " shutdown", "!",
        "ip route 192.168.90.0 255.255.255.192 192.168.90.137",
        "ip route 192.168.90.64 255.255.255.192 192.168.90.137",
        "ip route 192.168.90.128 255.255.255.252 192.168.90.137",
        "ip route 192.168.90.132 255.255.255.252 192.168.90.137",
        "ip route 192.168.90.148 255.255.255.252 192.168.90.146", "!",
        "end"], clocks={"Serial0/0/1"})

    r2 = router("1841", "R2", 1030, 200, {
        "FastEthernet0/0": ("192.168.90.149", "255.255.255.252", True),
        "FastEthernet0/1": ("", "", False),
        "Serial0/0/0": ("192.168.90.146", "255.255.255.252", True),
        "Serial0/0/1": ("", "", False),
    }, [
        "!", "hostname R2", "!",
        "interface Serial0/0/0", " ip address 192.168.90.146 255.255.255.252",
        " no shutdown", "!",
        "interface FastEthernet0/0", " ip address 192.168.90.149 255.255.255.252",
        " no shutdown", "!",
        "interface FastEthernet0/1", " no ip address", " shutdown", "!",
        "interface Serial0/0/1", " no ip address", " shutdown", "!",
        "ip route 0.0.0.0 0.0.0.0 192.168.90.145", "!",
        "end"])

    pc0 = pc("PC0", 180, 400, "192.168.90.10", "255.255.255.192", "192.168.90.1")
    pc1 = pc("PC1", 340, 400, "192.168.90.74", "255.255.255.192", "192.168.90.65")
    pc2 = pc("PC2", 790, 400, "192.168.90.142", "255.255.255.252", "192.168.90.141")
    pc3 = pc("PC3", 1030, 400, "192.168.90.150", "255.255.255.252", "192.168.90.149")
    pc4 = pc("PC4", 520, 40, "192.168.90.134", "255.255.255.252", "192.168.90.133")

    links = [
        B.make_link(0, "FastEthernet0/2", 4, "FastEthernet0"),
        B.make_link(0, "FastEthernet0/3", 5, "FastEthernet0"),
        B.make_link(0, "FastEthernet0/1", 1, "FastEthernet0/0"),
        B.make_link(1, "FastEthernet0/1", 8, "FastEthernet0", cable="eCrossOver"),
        B.make_link(1, "Serial0/0/0", 2, "Serial0/0/0", kind="eSerial", dce=1),
        B.make_link(2, "FastEthernet0/0", 6, "FastEthernet0", cable="eCrossOver"),
        B.make_link(2, "Serial0/0/1", 3, "Serial0/0/0", kind="eSerial", dce=2),
        B.make_link(3, "FastEthernet0/0", 7, "FastEthernet0", cable="eCrossOver"),
    ]
    notes = [
        (40, 40, "实验二  静态路由 + 3560 三层交换机\n"
                 "SW0 Fa0/1 用 no switchport 变三层口 = 192.168.90.129/30，R0 Fa0/0 = .130/30\n"
                 "VLAN2 192.168.90.0/26 网关 .1    VLAN3 192.168.90.64/26 网关 .65"),
        (40, 500, "验证：\n"
                  "PC0 ping 192.168.90.74  -> 通，TTL=127（SW0 三层转发，1 跳）\n"
                  "PC0 ping 192.168.90.134 -> 通，TTL=126（PC4，经 SW0、R0）\n"
                  "PC0 ping 192.168.90.142 -> 通，TTL=125（PC2，经 SW0、R0、R1）\n"
                  "PC0 ping 192.168.90.150 -> 通，TTL=124（PC3，经 SW0、R0、R1、R2）\n"
                  "PC0 tracert 192.168.90.150  -> .1  .130  .137  .138  .145  .146  .149\n"
                  "R2 用默认路由，其余设备全部为明细静态路由。"),
    ]
    save("90-实验二-静态路由与三层交换机.pkt",
         [sw, r0, r1, r2, pc0, pc1, pc2, pc3, pc4], links, notes)


# ================================================================== 实验三
def lab3():
    a = router("2621XM", "2621A", 220, 200, {
        "FastEthernet0/0": ("192.168.90.1", "255.255.255.224", True),
        "FastEthernet0/1": ("", "", False),
        "Serial0/0": ("", "", False),
        "Serial0/1": ("", "", False),
    }, [
        "!", "hostname 2621A", "!",
        "interface FastEthernet0/0", " ip address 192.168.90.1 255.255.255.224",
        " no shutdown", "!",
        "interface FastEthernet0/1", " no ip address", " shutdown", "!",
        "interface Serial0/0", " no ip address", " shutdown", "!",
        "interface Serial0/1", " no ip address", " shutdown", "!",
        "router rip", " network 192.168.90.0", "!",
        "end"])

    b = router("2621XM", "2501A", 480, 200, {
        "FastEthernet0/0": ("192.168.90.2", "255.255.255.224", True),
        "FastEthernet0/1": ("", "", False),
        "Serial0/0": ("192.168.90.33", "255.255.255.224", True),
        "Serial0/1": ("", "", False),
    }, [
        "!", "hostname 2501A", "!",
        "interface FastEthernet0/0", " ip address 192.168.90.2 255.255.255.224",
        " no shutdown", "!",
        "interface FastEthernet0/1", " no ip address", " shutdown", "!",
        "interface Serial0/0", " ip address 192.168.90.33 255.255.255.224",
        " clock rate 64000", " no shutdown", "!",
        "interface Serial0/1", " no ip address", " shutdown", "!",
        "router rip", " network 192.168.90.0", "!",
        "end"], clocks={"Serial0/0"})

    c = router("2621XM", "2501B", 740, 200, {
        "FastEthernet0/0": ("192.168.90.97", "255.255.255.224", True),
        "FastEthernet0/1": ("", "", False),
        "Serial0/0": ("192.168.90.34", "255.255.255.224", True),
        "Serial0/1": ("192.168.90.65", "255.255.255.224", True),
    }, [
        "!", "hostname 2501B", "!",
        "interface Serial0/0", " ip address 192.168.90.34 255.255.255.224",
        " no shutdown", "!",
        "interface Serial0/1", " ip address 192.168.90.65 255.255.255.224",
        " clock rate 64000", " no shutdown", "!",
        "interface FastEthernet0/0", " ip address 192.168.90.97 255.255.255.224",
        " no shutdown", "!",
        "interface FastEthernet0/1", " no ip address", " shutdown", "!",
        "router rip", " network 192.168.90.0", "!",
        "end"], clocks={"Serial0/1"})

    d = router("2621XM", "2501C", 1000, 200, {
        "FastEthernet0/0": ("192.168.90.129", "255.255.255.224", True),
        "FastEthernet0/1": ("", "", False),
        "Serial0/0": ("192.168.90.66", "255.255.255.224", True),
        "Serial0/1": ("", "", False),
    }, [
        "!", "hostname 2501C", "!",
        "interface Serial0/0", " ip address 192.168.90.66 255.255.255.224",
        " no shutdown", "!",
        "interface Serial0/1", " no ip address", " shutdown", "!",
        "interface FastEthernet0/0", " ip address 192.168.90.129 255.255.255.224",
        " no shutdown", "!",
        "interface FastEthernet0/1", " no ip address", " shutdown", "!",
        "router rip", " network 192.168.90.0", "!",
        "end"])

    p2 = pc("PC2", 740, 420, "192.168.90.98", "255.255.255.224", "192.168.90.97")
    p1 = pc("PC1", 1000, 420, "192.168.90.130", "255.255.255.224", "192.168.90.129")

    links = [
        B.make_link(0, "FastEthernet0/0", 1, "FastEthernet0/0", cable="eCrossOver"),
        B.make_link(1, "Serial0/0", 2, "Serial0/0", kind="eSerial", dce=1),
        B.make_link(2, "Serial0/1", 3, "Serial0/0", kind="eSerial", dce=2),
        B.make_link(2, "FastEthernet0/0", 4, "FastEthernet0", cable="eCrossOver"),
        B.make_link(3, "FastEthernet0/0", 5, "FastEthernet0", cable="eCrossOver"),
    ]
    notes = [
        (40, 40, "实验三  RIP 路由协议\n"
                 "原图机型 Cisco 2501，PT 8.2.2 无此型号 -> 统一用 2621XM + WIC-2T 替代\n"
                 "接口对照：原 Ethernet0 -> FastEthernet0/0；原 Serial0/Serial1 -> Serial0/0、Serial0/1\n"
                 "5 个网段统一 /27：.0  .32  .64  .96  .128"),
        (40, 500, "三阶段实验（本文件为第 1 阶段 RIPv1）：\n"
                  "1) 现状 router rip + network 192.168.90.0 -> show ip route 只看到 /24 汇总条目\n"
                  "2) 四台都加 version 2                     -> 路由表显示真实 /27\n"
                  "3) 四台都加 no auto-summary               -> 路由表出现 4 条明细 /27\n"
                  "每步都用 PC1 ping 192.168.90.98 验证连通（TTL=126）。"),
    ]
    save("90-实验三-RIP路由协议.pkt", [a, b, c, d, p2, p1], links, notes)


# ================================================================== 实验四
def lab4():
    def ospf_run(name, ports, nets, rid, dce):
        run = ["!", "hostname %s" % name, "!"]
        for pn in ["FastEthernet0/0", "FastEthernet0/1",
                   "Serial0/0/0", "Serial0/0/1"]:
            ip, mask = ports.get(pn, ("", ""))
            run.append("interface %s" % pn)
            if ip:
                run.append(" ip address %s %s" % (ip, mask))
                if pn in dce:
                    run.append(" clock rate 64000")
                run.append(" no shutdown")
            else:
                run.append(" no ip address")
                run.append(" shutdown")
            run.append("!")
        run += ["router ospf 1", " router-id %s" % rid, " log-adjacency-changes"]
        run += [" network %s area %d" % (n, ar) for n, ar in nets]
        run += ["!", "end"]
        return run

    def rtr(name, x, y, ports, nets, rid, dce=()):
        return router("1841", name, x, y,
                      {p: (v[0], v[1], bool(v[0])) for p, v in ports.items()},
                      ospf_run(name, ports, nets, rid, set(dce)), clocks=dce)

    r0 = rtr("R0", 240, 200, {
        "FastEthernet0/0": ("192.168.90.1", "255.255.255.192"),
        "FastEthernet0/1": ("", ""),
        "Serial0/0/0": ("192.168.90.197", "255.255.255.252"),
        "Serial0/0/1": ("192.168.90.193", "255.255.255.252"),
    }, [("192.168.90.0 0.0.0.63", 0), ("192.168.90.192 0.0.0.3", 0),
        ("192.168.90.196 0.0.0.3", 0)], "1.1.1.1",
        dce={"Serial0/0/0", "Serial0/0/1"})

    r1 = rtr("R1", 820, 200, {
        "FastEthernet0/0": ("192.168.90.65", "255.255.255.192"),
        "FastEthernet0/1": ("", ""),
        "Serial0/0/0": ("192.168.90.198", "255.255.255.252"),
        "Serial0/0/1": ("192.168.90.202", "255.255.255.252"),
    }, [("192.168.90.196 0.0.0.3", 0), ("192.168.90.200 0.0.0.3", 0),
        ("192.168.90.64 0.0.0.63", 1)], "2.2.2.2",
        dce={"Serial0/0/1"})

    r3 = rtr("R3", 530, 330, {
        "FastEthernet0/0": ("192.168.90.129", "255.255.255.192"),
        "FastEthernet0/1": ("", ""),
        "Serial0/0/0": ("192.168.90.194", "255.255.255.252"),
        "Serial0/0/1": ("192.168.90.201", "255.255.255.252"),
    }, [("192.168.90.192 0.0.0.3", 0), ("192.168.90.200 0.0.0.3", 0),
        ("192.168.90.128 0.0.0.63", 2)], "3.3.3.3")

    r2 = rtr("R2", 980, 400, {
        "FastEthernet0/0": ("192.168.90.66", "255.255.255.192"),
        "FastEthernet0/1": ("", ""),
        "Serial0/0/0": ("", ""),
        "Serial0/0/1": ("", ""),
    }, [("192.168.90.64 0.0.0.63", 1)], "4.4.4.4")

    r4 = rtr("R4", 760, 60, {
        "FastEthernet0/0": ("192.168.90.130", "255.255.255.192"),
        "FastEthernet0/1": ("", ""),
        "Serial0/0/0": ("", ""),
        "Serial0/0/1": ("", ""),
    }, [("192.168.90.128 0.0.0.63", 2)], "5.5.5.5")

    r5 = rtr("R5", 380, 60, {
        "FastEthernet0/0": ("192.168.90.131", "255.255.255.192"),
        "FastEthernet0/1": ("", ""),
        "Serial0/0/0": ("", ""),
        "Serial0/0/1": ("", ""),
    }, [("192.168.90.128 0.0.0.63", 2)], "6.6.6.6")

    def l2(kind, name, x, y, ports):
        run = ["!", "hostname %s" % name, "!"]
        for p in ports:
            run += ["interface FastEthernet0/%d" % p,
                    " switchport mode access", " switchport access vlan 1", "!"]
        run += ["end"]
        return switch(kind, name, x, y, None, run)

    sw0 = l2("2950-24", "Switch0", 240, 380, [1, 2])
    sw1 = l2("2950-24", "Switch1", 820, 380, [1, 2, 3])
    sw2 = l2("2960-24TT", "Switch2", 560, 100, [1, 2, 3, 4])

    pc0 = pc("PC0", 150, 500, "192.168.90.10", "255.255.255.192", "192.168.90.1")
    pc1 = pc("PC1", 820, 500, "192.168.90.74", "255.255.255.192", "192.168.90.65")
    pc2 = pc("PC2", 560, 200, "192.168.90.138", "255.255.255.192", "192.168.90.129")

    links = [
        B.make_link(0, "FastEthernet0/0", 6, "FastEthernet0/1"),   # R0 - Switch0
        B.make_link(6, "FastEthernet0/2", 9, "FastEthernet0"),     # Switch0 - PC0
        B.make_link(0, "Serial0/0/0", 1, "Serial0/0/0", kind="eSerial", dce=0),  # R0-R1
        B.make_link(0, "Serial0/0/1", 2, "Serial0/0/0", kind="eSerial", dce=0),  # R0-R3
        B.make_link(1, "Serial0/0/1", 2, "Serial0/0/1", kind="eSerial", dce=1),  # R1-R3
        B.make_link(1, "FastEthernet0/0", 7, "FastEthernet0/1"),   # R1 - Switch1
        B.make_link(7, "FastEthernet0/2", 3, "FastEthernet0/0"),   # Switch1 - R2
        B.make_link(7, "FastEthernet0/3", 10, "FastEthernet0"),    # Switch1 - PC1
        B.make_link(2, "FastEthernet0/0", 8, "FastEthernet0/3"),   # R3 - Switch2 Fa0/3
        B.make_link(8, "FastEthernet0/2", 5, "FastEthernet0/0"),   # Switch2 - R4
        B.make_link(8, "FastEthernet0/1", 4, "FastEthernet0/0"),   # Switch2 - R5
        B.make_link(8, "FastEthernet0/4", 11, "FastEthernet0"),    # Switch2 - PC2
    ]
    notes = [
        (40, 40, "实验四  OSPF 多区域\n"
                 "Area 0：R0、R1、R3        Area 1：R1(ABR)、Switch1、R2        "
                 "Area 2：R3(ABR)、Switch2、R4、R5\n"
                 "原图未画 PC，按任务要求补接 PC0 / PC1 / PC2\n"
                 "Switch2 接口照原图：Fa0/3->R3   Fa0/2->R4   Fa0/1->R5   Fa0/4->PC2"),
        (40, 600, "验证：\n"
                  "R0# show ip ospf neighbor   -> 2 个 FULL（R1、R3）\n"
                  "R1# show ip ospf neighbor   -> 2 个 FULL（R0、R3），ABR\n"
                  "R3# show ip ospf neighbor   -> 2 个 FULL（R0、R1），ABR\n"
                  "R2# show ip route ospf      -> O IA 的 Area0 / Area2 网段\n"
                  "PC0 ping PC1 / PC2 均通，TTL=126（各经 2 台路由器）"),
    ]
    save("90-实验四-OSPF多区域.pkt",
         [r0, r1, r3, r2, r5, r4, sw0, sw1, sw2, pc0, pc1, pc2], links, notes)


if __name__ == "__main__":
    B.MAC_SEQ[0] = 0
    lab1()
    lab2()
    lab3()
    lab4()
