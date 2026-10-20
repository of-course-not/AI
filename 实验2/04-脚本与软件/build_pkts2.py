# -*- coding: utf-8 -*-
"""生成实验二（ACL / NAT）的两个 Packet Tracer 工程文件。

拓扑、端口、地址全部按 05-原始资料 的原图与题目要求，
学号后两位 90，内网 192.168.90.0/24，公网 200.0.90.0/24。
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pktbuild as B
import pktlib

OUT = os.path.join(os.path.dirname(HERE), "03-工程文件")

_UID = [0]


def uid():
    _UID[0] += 1
    return 700000000 + _UID[0] * 7919


def remac(block):
    return re.sub(r"<(MACADDRESS|BIA)>[^<]*</\1>",
                  lambda m: "<%s>%s</%s>" % (m.group(1), B._mac(), m.group(1)), block)


def power_all(block, kind):
    names = B.port_names(kind, block)
    return B.set_ports(block, kind, {n: ("", "", True) for n in names})


# ---------------------------------------------------------------- 设备工厂

def router(kind, name, x, y, ports, run, clocks=()):
    b = B.donor_device(kind)
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
    if vlans:
        b = B.set_vlans(b, vlans)
    b = B.rename(b, name, x, y, uid())
    b = B.set_running(b, run)
    return b


def pc(name, x, y, ip, mask, gw):
    b = B.donor_device("PC-PT")
    b = remac(b)
    b = B.set_ports(b, "PC-PT", {"FastEthernet0": (ip, mask, True)})
    # PC-PT donor 里是自闭合的 <PORT_GATEWAY/>，正则必须同时匹配自闭合与成对写法
    b = re.sub(r"<PORT_GATEWAY\s*/>|<PORT_GATEWAY>[^<]*</PORT_GATEWAY>",
               "<PORT_GATEWAY>%s</PORT_GATEWAY>" % gw, b, count=1)
    b = re.sub(r"<GATEWAY\s*/>|<GATEWAY>[^<]*</GATEWAY>",
               "<GATEWAY>%s</GATEWAY>" % gw, b, count=1)
    b = B.rename(b, name, x, y, uid())
    run = ["!", "hostname %s" % name, "!", "end"]
    b = B.set_running(b, run)
    return b


def server(name, x, y, ip, mask, gw):
    # 必须用 6.1 格式的 Server-PT donor：5.2 版（HTTPS.pkt 抽出的）配 _base61 骨架
    # 会让 PT 打不开文件。Server-PT-61 抽自 traditional_netflow.pkt（VERSION 6.1.0.0026）。
    b = B.donor_device("Server-PT-61")
    b = remac(b)
    # Server-PT 只有一个 eCopperFastEthernet，且网关写在 ENGINE 级 <GATEWAY>
    b = re.sub(r"<POWER>[^<]*</POWER>", "<POWER>true</POWER>", b, count=1)
    b = re.sub(r"<IP/>|<IP>[^<]*</IP>", "<IP>%s</IP>" % ip, b, count=1)
    b = re.sub(r"<SUBNET/>|<SUBNET>[^<]*</SUBNET>", "<SUBNET>%s</SUBNET>" % mask, b, count=1)
    # 网关要同时写 ENGINE 级 <GATEWAY> 与 PORT 级 <PORT_GATEWAY>：
    # donor 的 PORT_GATEWAY 里残留着 13.1.1.1，两处不一致会让 PC 的默认网关取错值。
    b = re.sub(r"<GATEWAY\s*/>|<GATEWAY>[^<]*</GATEWAY>",
               "<GATEWAY>%s</GATEWAY>" % gw, b, count=1)
    b = re.sub(r"<PORT_GATEWAY\s*/>|<PORT_GATEWAY>[^<]*</PORT_GATEWAY>",
               "<PORT_GATEWAY>%s</PORT_GATEWAY>" % gw, b, count=1)
    b = B.rename(b, name, x, y, uid())
    run = ["!", "hostname %s" % name, "!", "end"]
    b = B.set_running(b, run)
    return b


def save(fn, devices, links, notes):
    path = os.path.join(OUT, fn)
    pktlib.save(path, B.build(devices, links, notes))
    print("saved:", fn, len(devices), "devices", len(links), "links")


# ================================================================ 实验二（一）ACL

def lab_acl():
    B.MAC_SEQ[0] = 0

    CORE_RUN = [
        "!", "version 12.2", "hostname CoreSW", "!",
        "ip routing",
        "!",
        "vlan 2", " name teacher",
        "vlan 3", " name stu",
        "vlan 4", " name server",
        "exit",
        "!",
        "interface FastEthernet0/1",
        " no switchport",
        " ip address 192.168.90.193 255.255.255.252",
        " no shutdown",
        "!",
        "interface FastEthernet0/2",
        " switchport mode access",
        " switchport access vlan 2",
        "!",
        "interface FastEthernet0/3",
        " switchport mode access",
        " switchport access vlan 2",
        "!",
        "interface FastEthernet0/4",
        " switchport mode access",
        " switchport access vlan 2",
        "!",
        "interface FastEthernet0/5",
        " switchport mode trunk",
        "!",
        "interface FastEthernet0/6",
        " switchport mode trunk",
        "!",
        "interface Vlan2",
        " ip address 192.168.90.1 255.255.255.192",
        " no shutdown",
        "!",
        "interface Vlan3",
        " ip address 192.168.90.65 255.255.255.192",
        " no shutdown",
        "!",
        "interface Vlan4",
        " ip address 192.168.90.129 255.255.255.192",
        " no shutdown",
        "!",
        "ip route 0.0.0.0 0.0.0.0 192.168.90.194",
        "!",
        "! ACL 110：VLAN4 out，控制去往服务器的流量（禁 ping、只许 teacher1 telnet）",
        "access-list 110 permit tcp host 192.168.90.10 192.168.90.128 0.0.0.63 eq 23",
        "access-list 110 deny tcp any 192.168.90.128 0.0.0.63 eq 23",
        "access-list 110 deny icmp any 192.168.90.128 0.0.0.63 echo",
        "access-list 110 permit ip any any",
        "! ACL 120：VLAN3 in，学生只能访问 Server0 的 web",
        "access-list 120 permit tcp 192.168.90.64 0.0.0.63 host 192.168.90.138 eq 80",
        "access-list 120 deny ip 192.168.90.64 0.0.0.63 192.168.90.128 0.0.0.63",
        "access-list 120 permit ip any any",
        "! ACL 130：VLAN4 in，服务器不能访问 Internet",
        "access-list 130 deny ip 192.168.90.128 0.0.0.63 200.0.90.0 0.0.0.255",
        "access-list 130 permit ip any any",
        "!",
        "interface Vlan4",
        " ip access-group 110 out",
        " ip access-group 130 in",
        "!",
        "interface Vlan3",
        " ip access-group 120 in",
        "!", "end"]

    STUDENT_RUN = [
        "!", "version 12.2", "hostname student", "!",
        "vlan 3", " name stu", "exit",
        "!",
        "interface FastEthernet0/1",
        " switchport mode access",
        " switchport access vlan 3",
        "!",
        "interface FastEthernet0/2",
        " switchport mode access",
        " switchport access vlan 3",
        "!",
        "interface FastEthernet0/3",
        " switchport mode access",
        " switchport access vlan 3",
        "!",
        "interface FastEthernet0/24",
        " switchport mode trunk",
        "!", "end"]

    SERVER_RUN = [
        "!", "version 12.2", "hostname Server", "!",
        "vlan 4", " name server", "exit",
        "!",
        "interface FastEthernet0/1",
        " switchport mode access",
        " switchport access vlan 4",
        "!",
        "interface FastEthernet0/2",
        " switchport mode access",
        " switchport access vlan 4",
        "!",
        "interface FastEthernet0/3",
        " switchport mode access",
        " switchport access vlan 4",
        "!",
        "interface FastEthernet0/24",
        " switchport mode trunk",
        "!", "end"]

    R0_RUN = [
        "!", "version 12.4", "hostname Router0", "!",
        "interface FastEthernet0/0",
        " ip address 192.168.90.194 255.255.255.252",
        " no shutdown",
        "!",
        "interface Serial0/0/0",
        " ip address 200.0.90.1 255.255.255.252",
        " clock rate 64000",
        " no shutdown",
        "!",
        "ip route 192.168.90.0 255.255.255.0 192.168.90.193",
        "ip route 0.0.0.0 0.0.0.0 200.0.90.2",
        "!", "end"]

    R1_RUN = [
        "!", "version 12.4", "hostname Router1", "!",
        "interface Serial0/0/0",
        " ip address 200.0.90.2 255.255.255.252",
        " no shutdown",
        "!",
        "interface Loopback0",
        " ip address 200.0.90.100 255.255.255.255",
        "!",
        "ip route 0.0.0.0 0.0.0.0 200.0.90.1",
        "!", "end"]

    devs = [
        switch("3560-24PS", "CoreSW", 280, 200,
               [(2, "teacher"), (3, "stu"), (4, "server")], CORE_RUN),          # 0
        pc("teacher1", 120, 70, "192.168.90.10", "255.255.255.192", "192.168.90.1"),   # 1
        pc("teacher2", 280, 50, "192.168.90.11", "255.255.255.192", "192.168.90.1"),   # 2
        pc("teacher3", 440, 70, "192.168.90.12", "255.255.255.192", "192.168.90.1"),   # 3
        switch("2960-24TT", "student", 280, 330, [(3, "stu")], STUDENT_RUN),   # 4
        pc("stu1", 170, 450, "192.168.90.74", "255.255.255.192", "192.168.90.65"),  # 5
        pc("stu2", 290, 470, "192.168.90.75", "255.255.255.192", "192.168.90.65"),  # 6
        pc("stu3", 410, 450, "192.168.90.76", "255.255.255.192", "192.168.90.65"),  # 7
        switch("2960-24TT", "Server", 620, 200, [(4, "server")], SERVER_RUN),  # 8
        server("Server0", 540, 330, "192.168.90.138", "255.255.255.192", "192.168.90.129"),  # 9
        server("Server1", 660, 350, "192.168.90.139", "255.255.255.192", "192.168.90.129"),  # 10
        server("Server2", 780, 330, "192.168.90.140", "255.255.255.192", "192.168.90.129"),  # 11
        router("1841", "Router0", 880, 110,
               {"FastEthernet0/0": ("192.168.90.194", "255.255.255.252", True),
                "Serial0/0/0": ("200.0.90.1", "255.255.255.252", True)},
               R0_RUN, clocks=["Serial0/0/0"]),                                # 12
        router("1841", "Router1", 1040, 110,
               {"Serial0/0/0": ("200.0.90.2", "255.255.255.252", True)}, R1_RUN),  # 13
    ]

    links = [
        B.make_link(0, "FastEthernet0/2", 1, "FastEthernet0"),
        B.make_link(0, "FastEthernet0/3", 2, "FastEthernet0"),
        B.make_link(0, "FastEthernet0/4", 3, "FastEthernet0"),
        B.make_link(0, "FastEthernet0/5", 4, "FastEthernet0/24"),
        B.make_link(4, "FastEthernet0/1", 5, "FastEthernet0"),
        B.make_link(4, "FastEthernet0/2", 6, "FastEthernet0"),
        B.make_link(4, "FastEthernet0/3", 7, "FastEthernet0"),
        B.make_link(0, "FastEthernet0/6", 8, "FastEthernet0/24"),
        B.make_link(8, "FastEthernet0/1", 9, "FastEthernet0"),
        B.make_link(8, "FastEthernet0/2", 10, "FastEthernet0"),
        B.make_link(8, "FastEthernet0/3", 11, "FastEthernet0"),
        B.make_link(0, "FastEthernet0/1", 12, "FastEthernet0/0"),
        B.make_link(12, "Serial0/0/0", 13, "Serial0/0/0", kind="eSerial", dce=12),
    ]

    notes = [
        (60, 620, "实验二（一）ACL 配置\n"
                  "VLAN2 teacher 192.168.90.0/26  GW .1\n"
                  "VLAN3 stu     192.168.90.64/26 GW .65\n"
                  "VLAN4 server  192.168.90.128/26 GW .129\n"
                  "核心交换机 Fa0/1 = 192.168.90.193/30，Router0 Fa0/0 = .194/30\n"
                  "ACL 挂在 CoreSW 的 SVI 上：Vlan3 in=120，Vlan4 in=130、out=110"),
        (60, 780, "验证顺序：show ip route → show access-lists →\n"
                  "PC 上 ping / 浏览器访问 http://192.168.90.138"),
    ]

    save("90-实验二一-ACL配置.pkt", devs, links, notes)


# ================================================================ 实验二（二）NAT

def lab_nat():
    B.MAC_SEQ[0] = 0

    CORE_RUN = [
        "!", "version 12.2", "hostname CoreSW", "!",
        "ip routing",
        "!",
        "vlan 2", " name teacher",
        "vlan 3", " name stu",
        "vlan 4", " name server",
        "exit",
        "!",
        "interface FastEthernet0/1",
        " no switchport",
        " ip address 192.168.90.193 255.255.255.252",
        " no shutdown",
        "!",
        "interface FastEthernet0/2",
        " switchport mode access",
        " switchport access vlan 2",
        "!",
        "interface FastEthernet0/3",
        " switchport mode access",
        " switchport access vlan 2",
        "!",
        "interface FastEthernet0/4",
        " switchport mode access",
        " switchport access vlan 2",
        "!",
        "interface FastEthernet0/5",
        " switchport mode trunk",
        "!",
        "interface FastEthernet0/6",
        " switchport mode trunk",
        "!",
        "interface Vlan2",
        " ip address 192.168.90.1 255.255.255.192",
        " no shutdown",
        "!",
        "interface Vlan3",
        " ip address 192.168.90.65 255.255.255.192",
        " no shutdown",
        "!",
        "interface Vlan4",
        " ip address 192.168.90.129 255.255.255.192",
        " no shutdown",
        "!",
        "ip route 0.0.0.0 0.0.0.0 192.168.90.194",
        "!", "end"]

    STUDENT_RUN = [
        "!", "version 12.2", "hostname student", "!",
        "vlan 3", " name stu", "exit",
        "!",
        "interface FastEthernet0/1",
        " switchport mode access",
        " switchport access vlan 3",
        "!",
        "interface FastEthernet0/2",
        " switchport mode access",
        " switchport access vlan 3",
        "!",
        "interface FastEthernet0/3",
        " switchport mode access",
        " switchport access vlan 3",
        "!",
        "interface FastEthernet0/24",
        " switchport mode trunk",
        "!", "end"]

    SERVER_RUN = [
        "!", "version 12.2", "hostname Server", "!",
        "vlan 4", " name server", "exit",
        "!",
        "interface FastEthernet0/1",
        " switchport mode access",
        " switchport access vlan 4",
        "!",
        "interface FastEthernet0/24",
        " switchport mode trunk",
        "!", "end"]

    NAT_RUN = [
        "!", "version 12.4", "hostname NAT路由器", "!",
        "interface FastEthernet0/0",
        " ip address 192.168.90.194 255.255.255.252",
        " ip nat inside",
        " no shutdown",
        "!",
        "interface Serial0/0/0",
        " ip address 200.0.90.1 255.255.255.252",
        " ip nat outside",
        " clock rate 64000",
        " no shutdown",
        "!",
        "ip route 192.168.90.0 255.255.255.0 192.168.90.193",
        "ip route 0.0.0.0 0.0.0.0 200.0.90.2",
        "!",
        "ip nat pool PUB 200.0.90.17 200.0.90.22 netmask 255.255.255.240",
        "access-list 1 permit 192.168.90.0 0.0.0.255",
        "ip nat inside source list 1 pool PUB",
        "ip nat inside source static tcp 192.168.90.138 80 200.0.90.30 80",
        "!", "end"]

    INET_RUN = [
        "!", "version 12.4", "hostname Internet路由器", "!",
        "interface Serial0/0/0",
        " ip address 200.0.90.2 255.255.255.252",
        " no shutdown",
        "!",
        "interface FastEthernet0/0",
        " ip address 200.0.90.9 255.255.255.248",
        " no shutdown",
        "!",
        "ip route 200.0.90.16 255.255.255.240 200.0.90.1",
        "!", "end"]

    OUTER_RUN = [
        "!", "version 12.2", "hostname 外网网络", "!",
        "vlan 10",
        " name outside",
        "exit",
        "!",
        "interface FastEthernet0/1",
        " switchport mode access",
        " switchport access vlan 10",
        "!",
        "interface FastEthernet0/2",
        " switchport mode access",
        " switchport access vlan 10",
        "!",
        "interface FastEthernet0/3",
        " switchport mode access",
        " switchport access vlan 10",
        "!", "end"]

    devs = [
        switch("3560-24PS", "CoreSW", 250, 190,
               [(2, "teacher"), (3, "stu"), (4, "server")], CORE_RUN),          # 0
        pc("teacher1", 100, 70, "192.168.90.10", "255.255.255.192", "192.168.90.1"),   # 1
        pc("teacher2", 250, 50, "192.168.90.11", "255.255.255.192", "192.168.90.1"),   # 2
        pc("teacher3", 400, 70, "192.168.90.12", "255.255.255.192", "192.168.90.1"),   # 3
        switch("2960-24TT", "student", 250, 320, [(3, "stu")], STUDENT_RUN),   # 4
        pc("stu1", 140, 440, "192.168.90.74", "255.255.255.192", "192.168.90.65"),  # 5
        pc("stu2", 260, 460, "192.168.90.75", "255.255.255.192", "192.168.90.65"),  # 6
        pc("stu3", 380, 440, "192.168.90.76", "255.255.255.192", "192.168.90.65"),  # 7
        switch("2960-24TT", "Server", 560, 320, [(4, "server")], SERVER_RUN),  # 8
        server("web服务器", 560, 440, "192.168.90.138", "255.255.255.192", "192.168.90.129"),  # 9
        router("1841", "NAT路由器", 560, 180,
               {"FastEthernet0/0": ("192.168.90.194", "255.255.255.252", True),
                "Serial0/0/0": ("200.0.90.1", "255.255.255.252", True)},
               NAT_RUN, clocks=["Serial0/0/0"]),                               # 10
        router("1841", "Internet路由器", 780, 180,
               {"Serial0/0/0": ("200.0.90.2", "255.255.255.252", True),
                "FastEthernet0/0": ("200.0.90.9", "255.255.255.248", True)}, INET_RUN),  # 11
        switch("2960-24TT", "外网网络", 960, 180, [(10, "outside")], OUTER_RUN),   # 12
        pc("外网用户", 890, 320, "200.0.90.11", "255.255.255.248", "200.0.90.9"),  # 13
        server("外网服务器", 1030, 320, "200.0.90.10", "255.255.255.248", "200.0.90.9"),  # 14
    ]

    links = [
        B.make_link(0, "FastEthernet0/2", 1, "FastEthernet0"),
        B.make_link(0, "FastEthernet0/3", 2, "FastEthernet0"),
        B.make_link(0, "FastEthernet0/4", 3, "FastEthernet0"),
        B.make_link(0, "FastEthernet0/5", 4, "FastEthernet0/24"),
        B.make_link(4, "FastEthernet0/1", 5, "FastEthernet0"),
        B.make_link(4, "FastEthernet0/2", 6, "FastEthernet0"),
        B.make_link(4, "FastEthernet0/3", 7, "FastEthernet0"),
        B.make_link(0, "FastEthernet0/6", 8, "FastEthernet0/24"),
        B.make_link(8, "FastEthernet0/1", 9, "FastEthernet0"),
        B.make_link(0, "FastEthernet0/1", 10, "FastEthernet0/0"),
        B.make_link(10, "Serial0/0/0", 11, "Serial0/0/0", kind="eSerial", dce=10),
        B.make_link(11, "FastEthernet0/0", 12, "FastEthernet0/1"),
        B.make_link(12, "FastEthernet0/2", 13, "FastEthernet0"),
        B.make_link(12, "FastEthernet0/3", 14, "FastEthernet0"),
    ]

    notes = [
        (60, 560, "实验二（二）NAT 配置\n"
                  "内网 192.168.90.0/24：VLAN2 .0/26 GW .1 / VLAN3 .64/26 GW .65 / VLAN4 .128/26 GW .129\n"
                  "公网 200.0.90.0/24：NAT-Internet .0/30，外网 LAN .8/29，公网池 .16/28\n"
                  "NAT路由器：Fa0/0 = ip nat inside，Se0/0/0 = ip nat outside"),
        (60, 720, "验证顺序：NAT路由器# show ip nat translations →\n"
                  "外网用户 ping 200.0.90.30（静态 PAT 到 web 服务器 80）"),
    ]

    save("90-实验二二-NAT配置.pkt", devs, links, notes)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    lab_acl()
    lab_nat()
