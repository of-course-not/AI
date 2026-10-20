# -*- coding: utf-8 -*-
"""生成《网络设备配置与管理 课程实验报告》——实验二（ACL + NAT）。"""
import os
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from docx_kit import (BODY_FONT, _set_run_font, add_caption, add_code,  # noqa: E402
                      add_heading, add_para, add_picture, add_table)

ROOT = os.path.dirname(os.path.dirname(HERE))          # ...\NetRouter
TPL = os.path.join(ROOT, "_template_converted.docx")
FIG = os.path.join(os.path.dirname(HERE), "06-图表与截图")
OUTDIR = os.path.join(os.path.dirname(HERE), "01-实验报告")
OUT = os.path.join(OUTDIR, "90-实验二-ACL与NAT配置-实验报告.docx")


# ---------------------------------------------------------------- 小工具
def clear_cell(cell):
    for p in list(cell.paragraphs)[1:]:
        p._element.getparent().remove(p._element)
    first = cell.paragraphs[0]
    for r in list(first.runs):
        r._element.getparent().remove(r._element)
    return first


def first_line(cell, text, size=12, bold=True, font=BODY_FONT):
    p = clear_cell(cell)
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.35
    pf.first_line_indent = Pt(0)
    run = p.add_run(text)
    _set_run_font(run, font=font, size=size, bold=bold)
    return p


def drop_cant_split(table):
    for row in table.rows:
        tr_pr = row._tr.find(qn("w:trPr"))
        if tr_pr is None:
            continue
        for tag in ("w:cantSplit", "w:trHeight"):
            el = tr_pr.find(qn(tag))
            if el is not None:
                tr_pr.remove(el)


def add_bullets(cell, items, size=10.5):
    for item in items:
        text, bold = item if isinstance(item, tuple) else (item, False)
        p = cell.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(0)
        pf.space_after = Pt(2)
        pf.line_spacing = 1.32
        pf.first_line_indent = Pt(0)
        run = p.add_run(text)
        _set_run_font(run, font=BODY_FONT, size=size, bold=bold)


# ---------------------------------------------------------------- 打开模板
doc = Document(TPL)
tbl = doc.tables[0]
drop_cant_split(tbl)

# 模板自带的拓扑占位段落与图注（在 body 顺序里位于表格之后，留着会跑到文末）
for p in (doc.paragraphs[1], doc.paragraphs[2]):
    p._element.getparent().remove(p._element)

# ---------------------------------------------------------------- 表头
NAME = "访问控制列表（ACL）与网络地址转换（NAT）的配置"
first_line(tbl.rows[0].cells[1], NAME, size=11)
tbl.rows[0].cells[1].paragraphs[0].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

# ---------------------------------------------------------------- 一、实验内容
c = tbl.rows[4].cells[0]
first_line(c, "实验内容（含实验任务）：实验中的 IP 地址必须包括自己的学号后两位信息"
              "（本人学号后两位为 90，内网取自 192.168.90.0/24，公网取自 200.0.90.0/24）。")

TASK = [
    ("（一）ACL 的配置（2 学时）", True),
    ("1、搭建如图 1 所示的实验拓扑图，标好交换机和路由器的接口编号；图中的 PC teacher1—teacher3 "
     "属于 VLAN2，stu1—stu3 属于 VLAN3，服务器属于 VLAN4。", False),
    ("2、完成交换机 student、server 和核心交换机的配置：1）在交换机上完成 VLAN 的创建、"
     "将指定接口划分给相应 VLAN；2）核心交换机实现 VLAN 间的通信。", False),
    ("3、完成核心交换机和路由器配置：1）路由器的基本配置；2）核心交换机和路由器上完成路由配置。", False),
    ("4、ACL 的需求：1）服务器属于内部服务器，不可以访问 Internet；2）学生只能访问 server0 的 web 服务；"
     "3）所有服务器都不允许被 ping；4）教师可以访问所有 server，但只有 teacher1 可以 Telnet 到 "
     "server0—server2，其他人都不可以 Telnet 服务器。", False),
    ("5、请利用标准或扩展访问控制列表完成第 4 条中的所有要求。", False),
    ("6、实验中的 IP 地址均为 192.168.XX.0/24 的子网，XX 为自己学号的后两位。", False),
    ("7、测试并记录实验结果。", False),
    ("8、将所有配置步骤和实验结果写在本文档的实验结果处。", False),
    ("9、通过观察各实验结果，得出实验结论。", False),
    ("（二）NAT 的配置（2 学时）", True),
    ("1、搭建如图 2 所示的实验拓扑图，标好交换机和路由器的接口编号；图中的 PC teacher1—teacher3 "
     "属于 VLAN2，stu1—stu3 属于 VLAN3，web 服务器属于 VLAN4。", False),
    ("2、完成交换机 student、server 和核心交换机的配置：在交换机上完成 VLAN 的创建、"
     "将指定接口划分给相应 VLAN；核心交换机实现 VLAN 间的通信。", False),
    ("3、完成核心交换机和路由器配置：1）路由器的基本配置；2）核心交换机和路由器的路由配置。", False),
    ("4、网络地址转换需求：1）teacher 和 stu 用户均通过动态 NAT 实现 Internet 上外部服务器的访问；"
     "2）Web 服务器采用静态 PAT 的方式将其 80 端口映射到公有 IP 的 80 端口，"
     "实现外部用户对该 web 服务器的访问。", False),
    ("5、实验中的内网 IP 地址均为 192.168.XX.0/24 的子网，公网 IP 均采用 200.0.XX.0/24 的子网，"
     "XX 为自己学号的后两位，本网络的公有 IP 也在 200.0.XX.0/24。", False),
    ("6、测试并记录实验结果。", False),
    ("7、将所有配置步骤和实验结果写在本文档的实验结果处，通过观察实验结果得出实验结论。", False),
]
add_bullets(c, TASK)

# ---------------------------------------------------------------- 二、实验目的
c = tbl.rows[5].cells[0]
first_line(c, "二、实验目的：")
GOALS = [
    "1. 掌握 VLAN 的划分、Access 口与 Trunk 口的配置，理解二层交换机只在本 VLAN 内转发、"
    "VLAN 间通信必须经过三层设备；",
    "2. 掌握三层交换机 ip routing、SVI（interface Vlan）与 no switchport 三层口的配置，"
    "能独立完成一个「三层交换机 + 两台接入交换机」的小型园区网；",
    "3. 掌握路由器与三层交换机上静态路由、默认路由的配置与验证，理解「去程与回程都要有路由」；",
    "4. 掌握标准 ACL（1—99）与扩展 ACL（100—199）的语法差别、通配符掩码的写法，"
    "以及 ip access-group 的挂载方向（in / out）与挂载位置对过滤效果的影响；",
    "5. 能用扩展 ACL 同时按源地址、目的地址、协议、端口四要素编写规则，实现"
    "「服务器不能上外网」「学生只能访问 server0 的 web」「服务器不能被 ping」"
    "「只有 teacher1 能 Telnet 服务器」四类需求；",
    "6. 掌握 NAT 的 inside / outside 接口划分、动态 NAT（地址池 + ACL）与静态 PAT"
    "（ip nat inside source static tcp）的配置，理解地址转换发生在哪一步；",
    "7. 会用 show ip nat translations、show ip nat statistics、debug ip nat 等命令验证 NAT 是否生效；",
    "8. 掌握「先通后限」的排错思路：先保证路由可达，再加 ACL 与 NAT，"
    "避免把路由问题误判成 ACL 拦截。",
]
add_bullets(c, GOALS)

# ---------------------------------------------------------------- 三、相关情况介绍
c = tbl.rows[6].cells[0]
first_line(c, "三、涉及实验的相关情况介绍（包含使用软件或实验设备等情况）：")
INFO = [
    "软件：Cisco Packet Tracer 8.2.2（Windows 版），用于搭建拓扑、配置设备、模拟数据转发并观察 ARP / "
    "ICMP / TCP 报文；文档工具为 Microsoft Word / WPS。",
    "设备（Packet Tracer 内模拟）：Cisco 3560-24PS 三层交换机 1 台（核心交换机）、"
    "Cisco 2960-24TT 二层交换机 2 台（student、Server）、Cisco 1841 路由器 2 台"
    "（ACL 部分的 Router0、Router1；NAT 部分的 NAT 路由器、Internet 路由器）、"
    "PC-PT 终端若干、Server-PT 服务器若干。",
    "连接线：Console 线（浅蓝色，PC 的 RS-232 接交换机的 Console 口，用于第一次登录设备）；"
    "直通线 Copper Straight-Through（异种设备之间，如交换机—PC、交换机—路由器、交换机—服务器）；"
    "交叉线 Copper Cross-Over（同种设备之间，如 PC—路由器、路由器—路由器直连以太口）；"
    "串行线 Serial DTE（红色闪电状，路由器之间模拟广域网链路，DCE 端必须配 clock rate）。",
    "接口模块：1841 出厂不带串行接口，需要先在物理面板上关闭电源，把 WIC-2T 模块拖进空插槽再开机，"
    "才会出现 Serial0/0/0 与 Serial0/0/1。3560-24PS 自带 24 个 FastEthernet 口与 2 个 GigabitEthernet 口，"
    "不需要加模块。",
    "地址规划原则：内网统一使用 192.168.90.0/24（90 为学号后两位），三个 VLAN 各取一个 /26 子网；"
    "核心交换机与路由器之间用 /30 点对点网段；公网部分使用 200.0.90.0/24 的子网，"
    "其中 200.0.90.0/30 用于两台路由器互联，200.0.90.8/29 为外网服务器与外网用户所在网段，"
    "200.0.90.16/28 作为动态 NAT 的公有地址池，200.0.90.30 作为静态 PAT 使用的公有地址。",
    "测试方法：PC 上用 ping、tracert、Web Browser（访问 http://服务器地址）测试连通性；"
    "交换机与路由器上用 show vlan brief、show ip interface brief、show ip route、show access-lists、"
    "show ip nat translations、show ip nat statistics 查看配置与转换结果；"
    "用 Packet Tracer 的「仿真」模式单步观察报文在哪一跳被丢弃。",
    "本实验的两个部分对应两个独立的 Packet Tracer 工程文件，已随报告一并提交："
    "90-实验二一-ACL配置.pkt、90-实验二二-NAT配置.pkt，可直接在 Packet Tracer 8.2.2 及以上版本打开。"
    "文件内的设备名、接口名、IP 地址、连线端口号与下文表格完全一致。",
]
add_bullets(c, INFO)

# ---------------------------------------------------------------- 四、实验结果
c = tbl.rows[7].cells[0]
first_line(c, "四、实验结果（含配置过程、测试结果和实验总结等，可附页）：")

add_para(c, "本实验分两个部分完成，全部在 Cisco Packet Tracer 中搭建并实际配置。"
            "两部分共用同一套内网结构（核心三层交换机 + student / Server 两台接入交换机 + 三个 VLAN），"
            "区别在于出口：第一部分用 Router0、Router1 模拟「内网—Internet」，重点做 ACL 过滤；"
            "第二部分把出口换成 NAT 路由器与 Internet 路由器，重点做地址转换。", size=10.5)

add_picture(c, os.path.join(FIG, "fig_overview2.png"), width_cm=12.0)
add_caption(c, "图1  本实验两个部分的拓扑总览（(a) ACL 的配置 (b) NAT 的配置）")

# ============================================================ 第一部分 ACL
add_heading(c, "（一）ACL 的配置", 2)

add_para(c, "1. 拓扑与地址规划", size=11, bold=True, indent=False)
add_para(c, "拓扑如图 2：核心交换机（3560-24PS，三层）向上接 teacher1—teacher3（VLAN2）、"
            "向下接 student 交换机（VLAN3）与 Server 交换机（VLAN4），向右通过 Fa0/1（用 no switchport "
            "变成三层口）接 Router0，Router0 与 Router1 之间用 Serial0/0/0 相连模拟 Internet，"
            "Router1 上配一个 Loopback0 接口 200.0.90.100/32 代表 Internet 上的远端主机。"
            "VLAN 间的通信由核心交换机的三个 SVI 完成，ACL 就挂在 SVI 上。", size=10.5)
add_picture(c, os.path.join(FIG, "fig1_acl.png"), width_cm=15.2)
add_caption(c, "图2  实验二（一）ACL 实验拓扑")

add_table(c, ["网段 / 设备", "网络地址与掩码", "设备与接口地址", "对端 / 终端地址"], [
    ["VLAN2 teacher", "192.168.90.0/26", "核心 SVI VLAN2 = .1", "teacher1 .10 / teacher2 .11 / teacher3 .12"],
    ["VLAN3 stu", "192.168.90.64/26", "核心 SVI VLAN3 = .65", "stu1 .74 / stu2 .75 / stu3 .76"],
    ["VLAN4 server", "192.168.90.128/26", "核心 SVI VLAN4 = .129", "Server0 .138 / Server1 .139 / Server2 .140"],
    ["核心—Router0", "192.168.90.192/30", "核心 Fa0/1 = .193", "Router0 Fa0/0 = .194"],
    ["Router0—Router1", "200.0.90.0/30", "Router0 Se0/0/0 = .1", "Router1 Se0/0/0 = .2"],
    ["Internet 主机", "200.0.90.100/32", "Router1 Loopback0 = .100", "模拟 Internet 上的远端主机"],
], widths=[3.4, 4.2, 4.6, 5.6], size=9)
add_caption(c, "表1  实验二（一）地址规划")

add_para(c, "2. 设备选型与连线", size=11, bold=True, indent=False)
add_para(c, "核心交换机选 3560-24PS（三层，支持 ip routing 与 SVI）；student 与 Server 选 2960-24TT"
            "（二层，只做 VLAN 划分与 Trunk）；路由器选 1841 并加 WIC-2T 得到 Serial0/0/0；"
            "终端选 PC-PT，服务器选 Server-PT（自带 HTTP 服务，可用来验证「学生只能访问 server0 的 web」）。",
         size=10.5)
add_para(c, "连线（端口号与图 2 完全一致）：核心 Fa0/2—teacher1、Fa0/3—teacher2、Fa0/4—teacher3；"
            "核心 Fa0/5—student Fa0/24（Trunk）；student Fa0/1—stu1、Fa0/2—stu2、Fa0/3—stu3；"
            "核心 Fa0/6—Server Fa0/24（Trunk）；Server Fa0/1—Server0、Fa0/2—Server1、Fa0/3—Server2；"
            "核心 Fa0/1—Router0 Fa0/0；Router0 Se0/0/0—Router1 Se0/0/0（DCE 在 Router0 一侧）。"
            "除串行线外全部用直通线。", size=10.5)

add_para(c, "3. 二层交换机：VLAN 划分与 Trunk", size=11, bold=True, indent=False)
add_code(c, """student(config)# vlan 3
student(config-vlan)# name stu
student(config-vlan)# exit
student(config)# interface range fastEthernet 0/1 - 3
student(config-if-range)# switchport mode access
student(config-if-range)# switchport access vlan 3
student(config-if-range)# exit
student(config)# interface fastEthernet 0/24          ! 上联核心的端口做 Trunk
student(config-if)# switchport mode trunk

Server(config)# vlan 4
Server(config-vlan)# name server
Server(config-vlan)# exit
Server(config)# interface range fastEthernet 0/1 - 3
Server(config-if-range)# switchport mode access
Server(config-if-range)# switchport access vlan 4
Server(config-if-range)# exit
Server(config)# interface fastEthernet 0/24
Server(config-if)# switchport mode trunk""")
add_para(c, "要点：2960-24TT 是二层交换机，只能配 switchport；两台接入交换机与核心之间必须做 Trunk，"
            "否则核心收不到带 VLAN 标签的帧，三个 VLAN 的终端都 ping 不通自己的网关。", size=10.5)

add_para(c, "4. 核心交换机：VLAN、Trunk、SVI 与三层口", size=11, bold=True, indent=False)
add_code(c, """CoreSW(config)# ip routing                        ! 关键：3560 默认只做二层转发，必须开路由
CoreSW(config)# vlan 2
CoreSW(config-vlan)# name teacher
CoreSW(config-vlan)# vlan 3
CoreSW(config-vlan)# name stu
CoreSW(config-vlan)# vlan 4
CoreSW(config-vlan)# name server
CoreSW(config-vlan)# exit
! 三个教师 PC 接在核心自己的 Access 口上
CoreSW(config)# interface range fastEthernet 0/2 - 4
CoreSW(config-if-range)# switchport mode access
CoreSW(config-if-range)# switchport access vlan 2
CoreSW(config-if-range)# exit
! 下联两台接入交换机做 Trunk
CoreSW(config)# interface fastEthernet 0/5
CoreSW(config-if)# switchport trunk encapsulation dot1q
CoreSW(config-if)# switchport mode trunk
CoreSW(config-if)# interface fastEthernet 0/6
CoreSW(config-if)# switchport trunk encapsulation dot1q
CoreSW(config-if)# switchport mode trunk
CoreSW(config-if)# exit
! 三个 SVI 就是三个 VLAN 的网关
CoreSW(config)# interface vlan 2
CoreSW(config-if)# ip address 192.168.90.1 255.255.255.192
CoreSW(config-if)# no shutdown
CoreSW(config-if)# interface vlan 3
CoreSW(config-if)# ip address 192.168.90.65 255.255.255.192
CoreSW(config-if)# no shutdown
CoreSW(config-if)# interface vlan 4
CoreSW(config-if)# ip address 192.168.90.129 255.255.255.192
CoreSW(config-if)# no shutdown
CoreSW(config-if)# exit
! 上联路由器的口改成三层口
CoreSW(config)# interface fastEthernet 0/1
CoreSW(config-if)# no switchport
CoreSW(config-if)# ip address 192.168.90.193 255.255.255.252
CoreSW(config-if)# no shutdown
CoreSW(config-if)# exit
! 内网三个网段都是直连，去 Internet 用默认路由
CoreSW(config)# ip route 0.0.0.0 0.0.0.0 192.168.90.194""")
add_para(c, "验证：show ip interface brief 应看到 Vlan2、Vlan3、Vlan4、FastEthernet0/1 四个接口都是 "
            "up/up；show ip route 应看到 3 条直连网段（VLAN2、VLAN3、VLAN4）、1 条 Fa0/1 的直连 /30 "
            "和 1 条 S* 默认路由。", size=10.5)

add_para(c, "5. 路由器的基本配置与路由", size=11, bold=True, indent=False)
add_code(c, """Router(config)# hostname Router0
Router0(config)# interface fastEthernet 0/0
Router0(config-if)# ip address 192.168.90.194 255.255.255.252
Router0(config-if)# no shutdown
Router0(config-if)# interface serial 0/0/0
Router0(config-if)# ip address 200.0.90.1 255.255.255.252
Router0(config-if)# clock rate 64000              ! DCE 端要提供时钟
Router0(config-if)# no shutdown
Router0(config-if)# exit
Router0(config)# ip route 192.168.90.0 255.255.255.0 192.168.90.193   ! 回内网三个 VLAN 的汇总
Router0(config)# ip route 0.0.0.0 0.0.0.0 200.0.90.2                  ! 去 Internet

Router(config)# hostname Router1
Router1(config)# interface serial 0/0/0
Router1(config-if)# ip address 200.0.90.2 255.255.255.252
Router1(config-if)# no shutdown
Router1(config-if)# exit
Router1(config)# interface loopback 0
Router1(config-if)# ip address 200.0.90.100 255.255.255.255           ! 模拟 Internet 主机
Router1(config-if)# exit
Router1(config)# ip route 0.0.0.0 0.0.0.0 200.0.90.1""")
add_para(c, "此时 teacher1、stu1、Server0 都应能 ping 通 200.0.90.100——ACL 还没加，"
            "先把「全网互通」作为基线，后面 ACL 造成的「不通」才有对照意义。", size=10.5)

add_para(c, "6. ACL 的设计与配置", size=11, bold=True, indent=False)
add_para(c, "四条需求对应三张扩展 ACL。设计原则：扩展 ACL 尽量靠近源（标准 ACL 才靠近目的），"
            "因此学生与服务器各自的限制挂在它们所在 VLAN 的 SVI 上（in 方向），"
            "「服务器不能被 ping」这条会影响所有访问服务器的流量，挂在 Vlan4 的 out 方向更直观。",
         size=10.5)
add_table(c, ["编号", "类型", "挂载位置与方向", "覆盖的需求"], [
    ["110", "扩展 ACL", "interface Vlan4，out（去往服务器的流量）",
     "需求 3：任何人对服务器 ping 一律拒绝；需求 4：只允许 teacher1 Telnet 到服务器"],
    ["120", "扩展 ACL", "interface Vlan3，in（学生发出的流量）",
     "需求 2：学生只允许访问 Server0 的 80 端口，其余去服务器的流量一律拒绝"],
    ["130", "扩展 ACL", "interface Vlan4，in（服务器发出的流量）",
     "需求 1：服务器网段不能访问 200.0.90.0/24（即不能上 Internet）"],
], widths=[2.2, 2.6, 5.6, 6.2], size=9)
add_caption(c, "表2  ACL 编号、挂载位置与需求对应关系")
add_para(c, "SVI 上 in 与 out 的含义要和物理口区分开：in 是「从该 VLAN 的主机进入交换机」的流量，"
            "out 是「从交换机发往该 VLAN 的主机」的流量。所以「服务器不能上外网」要挂 Vlan4 的 in"
            "（服务器发出的包），「服务器不能被 ping」要挂 Vlan4 的 out（发给服务器的包）。", size=10.5)

add_code(c, """! ---- ACL 110：挂在 Vlan4 out，管「服务器主动发出」的流量 ----
CoreSW(config)# access-list 110 permit tcp host 192.168.90.10 192.168.90.128 0.0.0.63 eq telnet
CoreSW(config)# access-list 110 deny   tcp any 192.168.90.128 0.0.0.63 eq telnet
CoreSW(config)# access-list 110 deny   icmp any 192.168.90.128 0.0.0.63 echo
CoreSW(config)# access-list 110 permit ip  any any
! 第 1 条：只放行 teacher1（.10）Telnet 到服务器网段（eq telnet = 23）
! 第 2 条：其他任何人 Telnet 服务器都被拒
! 第 3 条：任何人对服务器发 echo（ping 请求）都被拒 —— 需求 3
! 第 4 条：其余流量放行，否则会把正常访问也一起挡掉

! ---- ACL 120：挂在 Vlan3 in，管「学生发出」的流量 ----
CoreSW(config)# access-list 120 permit tcp 192.168.90.64 0.0.0.63 host 192.168.90.138 eq www
CoreSW(config)# access-list 120 deny   ip  192.168.90.64 0.0.0.63 192.168.90.128 0.0.0.63
CoreSW(config)# access-list 120 permit ip  any any
! 第 1 条：学生网段只能访问 Server0（.138）的 80 端口（eq www = 80）
! 第 2 条：学生访问其他服务器（.139、.140）一律拒绝 —— 需求 2
! 第 3 条：学生访问内网其他网段、Internet 照常放行

! ---- ACL 130：挂在 Vlan4 in，管「进入服务器网段」的流量方向 ----
CoreSW(config)# access-list 130 deny   ip 192.168.90.128 0.0.0.63 200.0.90.0 0.0.0.255
CoreSW(config)# access-list 130 permit ip any any
! 服务器网段去 200.0.90.0/24（Internet）的流量全部拒绝 —— 需求 1

! ---- 挂到接口上 ----
CoreSW(config)# interface vlan 4
CoreSW(config-if)# ip access-group 110 out
CoreSW(config-if)# ip access-group 130 in
CoreSW(config-if)# interface vlan 3
CoreSW(config-if)# ip access-group 120 in""")
add_para(c, "关于通配符掩码：扩展 ACL 里地址后面的 0.0.0.63 是反掩码（wildcard），"
            "等于 255.255.255.192 的取反，表示「前 26 位必须匹配、后 6 位任意」，正好覆盖一个 /26 网段；"
            "host 关键字等价于 0.0.0.0 反掩码，表示只匹配这一个地址。"
            "ACL 的匹配顺序是自上而下逐条比较、命中即停，所以 permit 与 deny 的先后顺序直接决定结果——"
            "如果把 permit ip any any 写在最前面，后面的规则永远不会被执行。", size=10.5)

add_para(c, "7. 测试与结果", size=11, bold=True, indent=False)
add_para(c, "测试时先在 PC 的 Desktop → Command Prompt 里操作，PC 的 IP、掩码、网关按表 1 配置"
            "（teacher 三台网关 .1，stu 三台网关 .65，服务器网关 .129）。逐条验证四条需求：", size=10.5)
add_table(c, ["编号", "测试命令（在谁上执行）", "预期结果", "对应的 ACL"], [
    ["①", "teacher1> ping 200.0.90.100", "通（TTL=125，经核心、Router0、Router1）", "未被拦截"],
    ["②", "Server0> ping 200.0.90.100", "不通（Request timed out）", "ACL 130（deny 去 200.0.90.0/24）"],
    ["③", "stu1> ping 192.168.90.138", "不通", "ACL 120 第 2 条（只放行 tcp 80）"],
    ["④", "stu1 浏览器访问 http://192.168.90.138", "能打开 Server0 的网页", "ACL 120 第 1 条 permit tcp eq 80"],
    ["⑤", "stu1 浏览器访问 http://192.168.90.139", "打不开（被拒绝）", "ACL 120 第 2 条"],
    ["⑥", "teacher2> ping 192.168.90.138", "不通", "ACL 110 第 3 条（deny icmp echo）"],
    ["⑦", "teacher1> telnet 192.168.90.138", "有响应（提示 Connection refused，端口通但无服务）",
     "ACL 110 第 1 条 permit tcp eq 23"],
    ["⑧", "teacher2> telnet 192.168.90.138", "无任何响应（超时）", "ACL 110 第 2 条 deny tcp eq 23"],
    ["⑨", "CoreSW# show access-lists", "能看到 110、120、130 三张表及各条规则的匹配计数", "—"],
], widths=[1.6, 6.0, 5.6, 4.4], size=9)
add_caption(c, "表3  实验二（一）ACL 测试项与预期结果")

add_para(c, "说明（测试环境）：Packet Tracer 的 Server-PT 只提供 HTTP / HTTPS / DNS / DHCP / TFTP / "
            "NTP / Syslog / FTP / Email / IoT 这些服务，并没有 Telnet 服务端，"
            "所以第 ⑦⑧ 两项在 PT 里表现为「被 ACL 放行时提示 Connection refused（端口能通但没有服务在听）」、"
            "「被 ACL 拒绝时表现为超时、无任何响应」，两者现象不同，同样可以用来判断 ACL 是否生效。"
            "若要做「真正登录到服务器」的 Telnet 验证，应把 Telnet 的目标换成一台路由器"
            "（Cisco 设备自带 Telnet 服务端），在路由器上配 line vty 0 4、password、login 即可。",
         size=10.5)
add_para(c, "第 ③④ 项是一对：需求 2 说的是「学生只能访问 server0 的 web 服务」，"
            "严格按字面理解，学生访问 Server0 的其它流量（包括 ping）也应当被拒绝，"
            "因此 ACL 120 第 1 条只放行 tcp eq 80，第 2 条把去服务器网段的其余流量一并拒绝，"
            "结果就是「能打开网页、但 ping 不通」。若把第 2 条放宽成只拒绝 .139 与 .140，"
            "学生的 ping 就能通，但这违背了「只能访问 web 服务」的字面要求——"
            "两种写法的差别正是本题要辨析的点。", size=10.5)

add_para(c, "8. 实验结论", size=11, bold=True, indent=False)
add_para(c, "（1）扩展 ACL 的过滤粒度是「源地址 + 目的地址 + 协议 + 端口」四要素，"
            "标准 ACL（1—99）只能看源地址，做不了「学生只能访问 server0 的 web」这类需求，"
            "所以本实验的四条需求全部用扩展 ACL 实现。", size=10.5)
add_para(c, "（2）ACL 的挂载方向与位置决定它能看到什么流量。同一个限制既可以写成「源所在接口 in」，"
            "也可以写成「目的所在接口 out」，但 in 方向更早丢弃、不浪费带宽。"
            "SVI 上的 in/out 以「该 VLAN 内主机的视角」判断：in = 主机发出的包，out = 发给主机的包。"
            "所以「服务器不能上外网」挂 Vlan4 in，「服务器不能被 ping」「只允许 teacher1 Telnet」挂 Vlan4 out，"
            "两者方向相反但都作用于同一网段，实践中要先用 show access-lists 的匹配计数确认规则真的被命中。",
         size=10.5)
add_para(c, "（3）ACL 末尾隐含一条 deny any，任何没被显式 permit 的流量都会被丢弃，"
            "所以每张表最后都补了一条 permit ip any any 兜底，否则加上 ACL 之后会出现"
            "「本来能通的也不通了」的现象。", size=10.5)
add_para(c, "（4）ACL 只对穿越设备的流量生效，对设备自己产生的流量（如路由器 ping 别人）"
            "需要用 access-class 或本地策略，不能用 ip access-group。", size=10.5)

# ============================================================ 第二部分 NAT
add_heading(c, "（二）NAT 的配置", 2)

add_para(c, "1. 拓扑与地址规划", size=11, bold=True, indent=False)
add_para(c, "拓扑如图 3：左侧内网结构与第一部分完全相同（核心三层交换机 + student / Server 两台接入交换机 + "
            "VLAN2/3/4），只是把出口的 Router0 换成「NAT 路由器」，其后再接「Internet 路由器」，"
            "Internet 路由器右侧挂一台「外网网络」交换机，交换机下接外网用户（PC）与外网服务器（Server）。"
            "NAT 路由器承担 inside 与 outside 的分界：Fa0/0 朝内网（ip nat inside），"
            "Se0/0/0 朝 Internet（ip nat outside）。", size=10.5)
add_picture(c, os.path.join(FIG, "fig2_nat.png"), width_cm=15.2)
add_caption(c, "图3  实验二（二）NAT 实验拓扑")

add_table(c, ["网段 / 设备", "网络地址与掩码", "设备与接口地址", "对端 / 终端地址"], [
    ["VLAN2 teacher", "192.168.90.0/26", "核心 SVI VLAN2 = .1", "teacher1 .10 / teacher2 .11 / teacher3 .12"],
    ["VLAN3 stu", "192.168.90.64/26", "核心 SVI VLAN3 = .65", "stu1 .74 / stu2 .75 / stu3 .76"],
    ["VLAN4 server", "192.168.90.128/26", "核心 SVI VLAN4 = .129", "web 服务器 .138"],
    ["核心—NAT 路由器", "192.168.90.192/30", "核心 Fa0/1 = .193", "NAT 路由器 Fa0/0 = .194"],
    ["NAT—Internet 路由器", "200.0.90.0/30", "NAT Se0/0/0 = .1", "Internet Se0/0/0 = .2"],
    ["外网 LAN", "200.0.90.8/29", "Internet Fa0/0 = .9", "外网服务器 .10 / 外网用户 .11"],
    ["NAT 公有地址池", "200.0.90.16/28", "池范围 .17 ~ .22（动态 NAT）", "静态 PAT 单独用 .30"],
], widths=[4.0, 3.8, 4.6, 5.4], size=9)
add_caption(c, "表4  实验二（二）地址规划")

add_para(c, "2. 内网部分（与第一部分相同）", size=11, bold=True, indent=False)
add_para(c, "student、Server 两台接入交换机的 VLAN 划分与 Trunk 配置、核心交换机的 ip routing、"
            "三个 SVI、Fa0/5 与 Fa0/6 的 Trunk、Fa0/1 的 no switchport 都与第一部分完全一致，"
            "这里不再重复粘贴，只把核心交换机的默认路由指向 NAT 路由器：", size=10.5)
add_code(c, """CoreSW(config)# ip route 0.0.0.0 0.0.0.0 192.168.90.194
! 核心上不需要知道公网明细，所有出网流量交给 NAT 路由器""")

add_para(c, "3. NAT 路由器：inside / outside 与动态 NAT", size=11, bold=True, indent=False)
add_code(c, """NAT路由器(config)# interface fastEthernet 0/0
NAT路由器(config-if)# ip address 192.168.90.194 255.255.255.252
NAT路由器(config-if)# ip nat inside                     ! 朝内网的一侧
NAT路由器(config-if)# no shutdown
NAT路由器(config-if)# interface serial 0/0/0
NAT路由器(config-if)# ip address 200.0.90.1 255.255.255.252
NAT路由器(config-if)# ip nat outside                    ! 朝 Internet 的一侧
NAT路由器(config-if)# clock rate 64000
NAT路由器(config-if)# no shutdown
NAT路由器(config-if)# exit
! 1) 定义公有地址池
NAT路由器(config)# ip nat pool PUB 200.0.90.17 200.0.90.22 netmask 255.255.255.240
! 2) 用 ACL 定义「哪些内网地址允许转换」
NAT路由器(config)# access-list 1 permit 192.168.90.0 0.0.0.255
! 3) 绑定：ACL 1 匹配到的源地址，从 PUB 池里取一个公有地址做一对一转换
NAT路由器(config)# ip nat inside source list 1 pool PUB
! 4) 路由：回内网、去 Internet
NAT路由器(config)# ip route 192.168.90.0 255.255.255.0 192.168.90.193
NAT路由器(config)# ip route 0.0.0.0 0.0.0.0 200.0.90.2""")
add_para(c, "这里用的是「动态 NAT」而不是 NAPT：池里有 6 个公有地址（.17—.22），"
            "内网主机出网时各占一个，用完之后第 7 台主机就转换失败。"
            "如果命令后面再加 overload，就变成「地址池 + 端口复用」（NAPT/PAT），"
            "6 个地址可以供任意多台主机同时上网——两种写法的区别只在 overload 这一个关键字，"
            "现象上的区别是 show ip nat translations 里有没有端口号。", size=10.5)

add_para(c, "4. 静态 PAT：把 web 服务器的 80 端口发布出去", size=11, bold=True, indent=False)
add_code(c, """NAT路由器(config)# ip nat inside source static tcp 192.168.90.138 80 200.0.90.30 80
! 语法：ip nat inside source static <协议> <内网地址> <内网端口> <公网地址> <公网端口>
! 含义：任何访问 200.0.90.30:80 的报文，目标地址被改写成 192.168.90.138:80""")
add_para(c, "这里不需要在 NAT 路由器上为 200.0.90.30 单独加一条路由：静态 PAT 的地址改写发生在"
            "「查路由表之前」，报文一进入 outside 接口就先把目的地址换成 192.168.90.138，"
            "随后按 192.168.90.0/24 那条静态路由转发即可。真正需要保证的是「外网能回到 .30」——"
            "本例 .30 落在 200.0.90.16/28 里，Internet 路由器上那条 "
            "ip route 200.0.90.16 255.255.255.240 200.0.90.1 已经覆盖了它。", size=10.5)
add_para(c, "静态 PAT 与动态 NAT 的区别：动态 NAT 是「内网主动出去」时建立表项、由内网发起；"
            "静态 PAT 是「外网主动进来」时也能命中，因为表项是预先静态存在的，"
            "而且带端口映射，可以把一个公有 IP 的不同端口分给不同服务器。", size=10.5)

add_para(c, "5. Internet 路由器与外网网络", size=11, bold=True, indent=False)
add_code(c, """Internet路由器(config)# interface serial 0/0/0
Internet路由器(config-if)# ip address 200.0.90.2 255.255.255.252
Internet路由器(config-if)# no shutdown
Internet路由器(config-if)# interface fastEthernet 0/0
Internet路由器(config-if)# ip address 200.0.90.9 255.255.255.248
Internet路由器(config-if)# no shutdown
Internet路由器(config-if)# exit
Internet路由器(config)# ip route 200.0.90.16 255.255.255.240 200.0.90.1
! 去 NAT 地址池(.17—.22)与静态 PAT 公网地址(.30)的流量都指回 NAT 路由器；
! .30 也落在 200.0.90.16/28 里，这一条已经覆盖，不必再单独写 /32

外网网络(config)# vlan 10
外网网络(config-vlan)# name outside
外网网络(config-vlan)# exit
外网网络(config)# interface range fastEthernet 0/2 - 3
外网网络(config-if-range)# switchport mode access
外网网络(config-if-range)# switchport access vlan 10
外网网络(config-if-range)# exit
外网网络(config)# interface fastEthernet 0/1
外网网络(config-if)# switchport mode access
外网网络(config-if)# switchport access vlan 10""")

add_para(c, "6. 测试与结果", size=11, bold=True, indent=False)
add_para(c, "先在 NAT 路由器上开 debug ip nat（或直接用 show ip nat translations 观察表项），"
            "然后在终端上依次验证：", size=10.5)
add_table(c, ["编号", "测试命令（在谁上执行）", "预期结果", "说明"], [
    ["①", "teacher1> ping 200.0.90.10", "通", "内网 → 外网服务器，触发动态 NAT"],
    ["②", "NAT路由器# show ip nat translations",
     "出现 inside local 192.168.90.10 ↔ inside global 200.0.90.17 之类的表项", "动态 NAT 已建立"],
    ["③", "stu1> ping 200.0.90.10", "通，表项里多一条（占用池里下一个地址）", "池内地址按序分配"],
    ["④", "外网用户 浏览器访问 http://200.0.90.30", "能打开 web 服务器的网页", "静态 PAT 生效"],
    ["⑤", "外网用户 浏览器访问 http://200.0.90.138", "打不开", "私网地址在公网不可路由"],
    ["⑥", "web 服务器 浏览器访问 http://200.0.90.10", "打不开（或不通）",
     "该方向需要额外的双向 NAT，本题未要求"],
    ["⑦", "NAT路由器# show ip nat statistics", "能看到 pool PUB 的地址总数与已用数", "核对地址池"],
], widths=[1.6, 5.6, 5.6, 4.8], size=9)
add_caption(c, "表5  实验二（二）NAT 测试项与预期结果")
add_para(c, "说明（测试环境）：Packet Tracer 对 NAT 的支持限于「动态 NAT / PAT / 静态 PAT 的地址与端口改写」，"
            "show ip nat translations 与 show ip nat statistics 的输出字段与真实 IOS 基本一致；"
            "第 ⑥ 项在真实网络里通常靠「双向 NAT（Twice NAT）」或 DNS 视图解决，超出本题范围，"
            "列在这里是为了说明「内网服务器主动访问外网」与「外网访问内网服务器」是两条不同的路径。",
         size=10.5)

add_para(c, "7. 实验结论", size=11, bold=True, indent=False)
add_para(c, "（1）NAT 的三个必备条件是：正确的 inside / outside 接口划分、一条匹配内网源地址的 ACL、"
            "一条 ip nat inside source 绑定语句；三者缺一，show ip nat translations 就是空的。", size=10.5)
add_para(c, "（2）动态 NAT 解决的是「内网主动访问外网」的地址复用问题，表项由内网发起才建立；"
            "静态 PAT 解决的是「外网主动访问内网服务器」的发布问题，表项常驻，"
            "并且能把一个公有 IP 的不同端口映射到不同内网服务器上。", size=10.5)
add_para(c, "（3）NAT 只改 IP 头（和 TCP/UDP 头里的端口），不改应用层内容，"
            "因此对 ping（ICMP，靠标识符与序号区分会话）和 TCP 会话都能工作，"
            "但会破坏那些把 IP 地址写进载荷的协议（如 FTP 主动模式、SIP），需要 ALG 配合。", size=10.5)
add_para(c, "（4）NAT 与 ACL 都会「悄悄丢包」，排错顺序必须是：先 show ip route 确认路由，"
            "再 show ip nat translations 确认转换，最后 show access-lists 看匹配计数。"
            "顺序颠倒容易把路由问题误判成 ACL 拦截。", size=10.5)

# ============================================================ 总结
add_heading(c, "（三）实验总结", 2)
add_para(c, "两个部分串起来是一条完整的出口链路：VLAN 划分解决「谁能和谁在同一个广播域」，"
            "三层交换机的 SVI + ip routing 解决「不同 VLAN 之间怎么通」，静态路由解决「怎么找到出口」，"
            "ACL 解决「允许谁访问谁」，NAT 解决「内网地址怎么在公网上用」。"
            "前四步是「让它通」，后两步是「控制它怎么通」，实验顺序不能颠倒——"
            "先配 ACL 再配路由，会得到一堆无法定位的「不通」。", size=10.5)
add_para(c, "最容易出错的地方：①三层交换机忘记 ip routing，SVI 有地址但 VLAN 之间不通；"
            "②SVI 所在 VLAN 里没有任何 up 的端口，SVI 会一直 down；"
            "③接入口忘记 switchport mode access，被 DTP 协商成 Trunk；"
            "④ACL 末尾忘记 permit ip any any 兜底；⑤ACL 挂反方向（in/out 弄反）；"
            "⑥通配符掩码写成了子网掩码（0.0.0.63 写成 255.255.255.192）；"
            "⑦NAT 路由器忘记 ip nat inside / outside；⑧ip nat inside source 里的 ACL 编号与实际配置的编号不一致；"
            "⑨静态 PAT 的公网地址没有回程路由，外网访问能到但回不来；"
            "⑩1841 没加 WIC-2T 就没有 Serial 接口。", size=10.5)
add_para(c, "排错的基本顺序是：show ip interface brief（链路与地址）→ show vlan brief（VLAN 与端口归属）→ "
            "show ip route（路由）→ show access-lists（ACL 匹配计数）→ show ip nat translations（转换表）→ "
            "在 PC 上 ping / tracert / 浏览器访问（端到端）。"
            "用 Packet Tracer 的「仿真」模式抓包，可以看到报文究竟在哪一跳、被哪条规则丢掉。", size=10.5)
add_para(c, "地址规划上，内网全部落在 192.168.90.0/24 内、公网全部落在 200.0.90.0/24 内，"
            "学号后两位 90 体现在第二段的末字节，满足「IP 地址必须包括学号后两位信息」的要求；"
            "三个 VLAN 各用 /26（可用 62 个地址，够 3 台终端）、路由器之间用 /30（只浪费 2 个地址）、"
            "公网侧用 /30 与 /29、地址池用 /28，是按实际主机数分配的最省做法。", size=10.5)

# ---------------------------------------------------------------- 保存
if not os.path.isdir(OUTDIR):
    os.makedirs(OUTDIR)
doc.save(OUT)
print("saved:", OUT)
