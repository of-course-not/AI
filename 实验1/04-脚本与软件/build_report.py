# -*- coding: utf-8 -*-
"""Build the finished experiment report from the school template."""
import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

from docx_kit import (BODY_FONT, HEAD_FONT, _set_run_font, add_caption, add_code,
                      add_heading, add_para, add_picture, add_table, set_cell_lines)

HERE = os.path.dirname(os.path.abspath(__file__))   # ...\实验1\04-脚本与软件
EXP1 = os.path.dirname(HERE)                        # ...\实验1
TPL = os.path.join(EXP1, "05-原始资料", "_template_converted.docx")
FIG = os.path.join(EXP1, "06-图表与截图")
OUT = os.path.join(EXP1, "01-实验报告",
                   "90-实验一-路由器配置与路由协议-实验报告.docx")

# ---------------------------------------------------------------- helpers
def clear_cell(cell):
    """Keep the first paragraph, drop everything else."""
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
    """Let long cells flow across pages."""
    for row in table.rows:
        tr_pr = row._tr.find(qn("w:trPr"))
        if tr_pr is None:
            continue
        for tag in ("w:cantSplit", "w:trHeight"):
            el = tr_pr.find(qn(tag))
            if el is not None:
                tr_pr.remove(el)


def tie_caption(table):
    """Keep the table's last row on the same page as the caption below it."""
    for cell in table.rows[-1].cells:
        for p in cell.paragraphs:
            p.paragraph_format.keep_with_next = True


def drop_empty_table_row(table, index):
    row = table.rows[index]
    row._tr.getparent().remove(row._tr)


# ---------------------------------------------------------------- open template
doc = Document(TPL)
tbl = doc.tables[0]
drop_cant_split(tbl)

# ---- the template's old topology placeholder (P1 + its caption P2) is removed;
# the overview figure is inserted at the head of the results section instead,
# because those two paragraphs sit *after* the table in body order.
for p in (doc.paragraphs[1], doc.paragraphs[2]):
    p._element.getparent().remove(p._element)

# ---------------------------------------------------------------- 表头信息
NAME = "路由器基本配置与静态路由、RIP、OSPF 配置"

first_line(tbl.rows[0].cells[1], NAME, size=11)
tbl.rows[0].cells[1].paragraphs[0].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
tbl.rows[1].cells[1].paragraphs[0].add_run("")          # 姓名（留空自填）
tbl.rows[1].cells[3].paragraphs[0].add_run("")          # 学号（留空自填）
tbl.rows[1].cells[5].paragraphs[0].add_run("")          # 班级（留空自填）
tbl.rows[2].cells[1].paragraphs[0].add_run("")          # 实验地点
tbl.rows[2].cells[3].paragraphs[0].add_run("")          # 实验日期

# ---------------------------------------------------------------- 一、实验内容
c = tbl.rows[4].cells[0]
first_line(c, "实验内容（含实验任务）：实验涉及的 IP 地址必须包括自己的学号后两位信息"
              "（本人学号后两位为 90，故全部网段取自 192.168.90.0/24）。")

TASK = [
    ("（一）路由器基本配置（2 学时）", True),
    ("1、设计并构建实验拓扑图。", False),
    ("2、通过路由器 console 口连接完成基本配置：", False),
    ("1）练习并掌握路由器的各种模式切换（enable、configure terminal、interface）；", False),
    ("2）练习路由器基本配置：?（帮助）、hostname、clock、banner、copy、show running-config、show ip route；", False),
    ("3）配置环回接口（interface loopback 0; ip address ...）、局域网接口（interface fa0/0; ip address ...; "
     "no shutdown）和添加广域网模块、配置广域网接口（interface serial0/0/0; ip address ...; no shutdown），"
     "并用 show ip route 查看配置结果；", False),
    ("4）练习 telnet 远程访问配置（line vty 0 4、login、password，以及特权模式密码 enable password 或 "
     "enable secret），并测试 telnet 配置（用其他 PC 通过 telnet 登录到路由器，实现远程管理）。", False),
    ("3、自己设计拓扑，完成单臂路由器的 VLAN（至少 2 个 VLAN）间的通信。", False),
    ("4、将配置步骤和结果写在实验报告处。", False),
    ("（二）静态路由（2 学时）", True),
    ("1、拓扑如图 1（本报告图 3），IP 自规划，必须含学号后两位。", False),
    ("2、三层交换机配置：1）ip routing（启动路由功能）；2）创建 vlan2 和 vlan3，将 Fa0/2 划入 VLAN2、"
     "Fa0/3 划入 VLAN3；3）interface vlan 2; ip address ...; no shutdown（VLAN3 同理）；"
     "4）将 Fa0/1 设置为三层口（no switchport; ip address ...）；5）在三层交换机上配置静态路由"
     "（ip route 目的网络 掩码 下一跳）。", False),
    ("3、所有路由器配置：1）基本配置；2）静态路由配置（ip route）。", False),
    ("4、PC 配置（IP、掩码、网关）。", False),
    ("5、测试全网连通性。", False),
    ("6、将配置步骤和结果写入报告。", False),
    ("（三）RIP（2 学时）", True),
    ("1、拓扑如图 2（本报告图 4），XX 为学号后两位。", False),
    ("2、所有路由器配置：1）基本配置；2）RIPv1 配置（router rip; network）。", False),
    ("3、PC 配置。", False),
    ("4、测试全网连通性。", False),
    ("5、将 RIP 协议配置为版本 2，测试全网连通性。", False),
    ("6、关闭所有路由器的自动汇总功能，测试全网连通性。", False),
    ("7、将配置步骤和结果写入报告。", False),
    ("（四）OSPF（2 学时）", True),
    ("1、拓扑如图 3（本报告图 5），IP 为 192.168.XX.0 网络的子网（XX 为学号后两位）。", False),
    ("2、所有路由器配置：1）基本配置；2）OSPF 配置（router ospf 1; network）。", False),
    ("3、PC 配置。", False),
    ("4、测试全网连通性。", False),
    ("5、将配置步骤和结果写入报告。", False),
    ("6、观察实验结果得出实验结论。", False),
]
for text, bold in TASK:
    p = c.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(2)
    pf.line_spacing = 1.32
    pf.first_line_indent = Pt(0)
    run = p.add_run(text)
    _set_run_font(run, font=BODY_FONT, size=10.5, bold=bold)

# ---------------------------------------------------------------- 二、实验目的
c = tbl.rows[5].cells[0]
first_line(c, "二、实验目的：")
GOALS = [
    "1. 掌握 Cisco Packet Tracer 中路由器、交换机与 PC 的选型、连线（直通线/交叉线/串行线/console 线）"
    "以及通过 console 口登录设备的方法；",
    "2. 掌握路由器命令行各种操作模式（用户模式、特权模式、全局配置模式、接口模式）的切换，"
    "会用 ? 获取帮助，会做 hostname、clock、banner、copy、show running-config、show ip route 等基本配置与查看；",
    "3. 掌握环回接口、以太网接口、串行（广域网）接口的地址配置与 no shutdown 的作用，"
    "理解直连路由在 show ip route 中的出现条件；",
    "4. 掌握 telnet 远程管理的配置（line vty、login、password、enable secret）与测试方法；",
    "5. 掌握单臂路由（一个物理接口 + 多个 802.1Q 子接口）实现 VLAN 间通信的原理与配置；",
    "6. 掌握三层交换机 ip routing、SVI、no switchport 三层口的使用，以及静态路由的配置与验证；",
    "7. 掌握 RIPv1 与 RIPv2 的配置差异（version 2、no auto-summary），理解有类/无类路由与自动汇总的影响；",
    "8. 掌握 OSPF 单区域与多区域的配置（router ospf、network、area），理解 ABR 与区域划分的作用。",
]
for text in GOALS:
    p = c.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(2)
    pf.line_spacing = 1.32
    pf.first_line_indent = Pt(0)
    run = p.add_run(text)
    _set_run_font(run, font=BODY_FONT, size=10.5)

# ---------------------------------------------------------------- 三、相关情况介绍
c = tbl.rows[6].cells[0]
first_line(c, "三、涉及实验的相关情况介绍（包含使用软件或实验设备等情况）：")
INFO = [
    "软件：Cisco Packet Tracer 8.x（Windows 版），用于搭建拓扑、配置设备并抓包/测试；"
    "文档工具为 Microsoft Word / WPS。",
    "设备（Packet Tracer 内模拟）：Cisco 1841 路由器、Cisco 2621XM 路由器、"
    "Cisco 3560-24PS 三层交换机、Cisco 2960-24TT 与 2950-24 二层交换机、PC-PT 终端。",
    "连接线：Console 线（浅蓝色，PC 的 RS-232 接路由器的 Console 口）、直通线 Copper Straight-Through"
    "（异种设备之间，如路由器—交换机、交换机—PC）、交叉线 Copper Cross-Over（同种设备之间）、"
    "串行线 Serial DTE（红色，DCE 端需配 clock rate）。",
    "接口模块：1841 出厂不带串行接口，需在物理面板先关闭电源，再把 WIC-2T 模块拖入插槽，"
    "开机后才会出现 Serial0/0/0、Serial0/0/1；2621XM 同样不自带串口，插一块 WIC-2T 得到 "
    "Serial0/0、Serial0/1，插两块得到 Serial0/0～Serial0/3，以太口为 FastEthernet0/0、FastEthernet0/1。",
    "机型替代说明：原图 2 标注的 Cisco 2501 在 Packet Tracer 8.2.2 中已不再提供（设备面板与帮助文档"
    "均无此型号），故本实验用 2621XM + WIC-2T 替代。对应关系：原图 Ethernet0（E0）→ FastEthernet0/0；"
    "原图 Serial0（S0）→ Serial0/0；原图 Serial1（S1）→ Serial0/1。拓扑结构与地址规划完全不变。",
    "地址规划原则：全部地址落在 192.168.90.0/24 内（学号后两位 90）。局域网段用 /26，"
    "路由器之间的点对点链路与 PC 直连段用 /30；RIP 实验因 RIPv1 不通告掩码，5 个网段统一用 /27。",
    "测试方法：PC 的 Command Prompt 中 ping / tracert；路由器上 show ip interface brief、"
    "show ip route、show ip protocols、show ip ospf neighbor、debug ip rip 等命令验证。",
]
for text in INFO:
    p = c.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(2)
    pf.line_spacing = 1.32
    pf.first_line_indent = Pt(0)
    run = p.add_run(text)
    _set_run_font(run, font=BODY_FONT, size=10.5)

# ---------------------------------------------------------------- 四、实验结果
c = tbl.rows[7].cells[0]
first_line(c, "四、实验结果（含配置过程、测试结果和实验总结等，可附页）：")

add_para(c, "本实验分四个部分完成，全部在 Cisco Packet Tracer 中搭建并实际配置、测试。"
            "四个部分使用同一套地址规划思路：主网 192.168.90.0/24（90 为学号后两位），"
            "每个实验内部按需再分子网，互不冲突（不同实验是各自独立的工程文件）。",
         size=10.5, indent=True)
add_para(c, "四个部分对应四个独立的 Packet Tracer 工程文件（已随报告一并提交，可直接在 "
            "Packet Tracer 8.2.2 及以上版本打开）：90-实验一-路由器基本配置与单臂路由.pkt、"
            "90-实验二-静态路由与三层交换机.pkt、90-实验三-RIP路由协议.pkt、90-实验四-OSPF多区域.pkt。"
            "每个文件内的设备名、接口名、IP 地址、连线端口号与下文表格完全一致，"
            "打开后按各小节给出的验证命令逐条检查即可复现全部测试结果。",
         size=10.5, indent=True)

add_picture(c, os.path.join(FIG, "fig_overview.png"), width_cm=15.6)
add_caption(c, "图1  本实验四个部分的拓扑总览（(a) 基本配置与单臂路由 (b) 静态路由与三层交换机 "
               "(c) RIP (d) OSPF）")

# ============================================================ 实验一
add_heading(c, "（一）路由器基本配置与单臂路由", 2)

add_para(c, "1. 实验拓扑与地址规划", size=11, bold=True, indent=False)
add_para(c, "自行设计的拓扑如图 2：R1 通过 Fa0/0 连接二层交换机 SW1，SW1 上划分 VLAN10 与 VLAN20，"
            "两个 PC 分别属于不同 VLAN；R1 在 Fa0/0 上建立两个子接口 Fa0/0.10、Fa0/0.20 做单臂路由，"
            "使 VLAN10 与 VLAN20 互通。R1 另配 Loopback0 用于练习环回接口，R1 与 R2 之间用 Serial0/0/0 "
            "相连（练习广域网接口与 WIC-2T 模块），R2 的 Fa0/0 接 PC-C。",
         size=10.5)
add_picture(c, os.path.join(FIG, "fig0_basic.png"), width_cm=13.5)
add_caption(c, "图2  实验一拓扑：单臂路由 + 环回接口 + 串行接口")

add_table(c, ["网段", "网络地址/掩码", "设备与接口地址", "对端/PC 地址"], [
    ["VLAN10", "192.168.90.0/26", "R1 Fa0/0.10 = .1", "PC-A = .10"],
    ["VLAN20", "192.168.90.64/26", "R1 Fa0/0.20 = .65", "PC-B = .74"],
    ["R1—R2", "192.168.90.128/30", "R1 Se0/0/0 = .129", "R2 Se0/0/0 = .130"],
    ["PC-C 段", "192.168.90.132/30", "R2 Fa0/0 = .133", "PC-C = .134"],
    ["Loopback0", "192.168.90.200/32", "R1 Lo0 = .200", "—"],
], widths=[3.0, 4.6, 5.2, 4.0], size=9)
add_caption(c, "表1  实验一地址规划")

add_para(c, "2. 设备选型与连线", size=11, bold=True, indent=False)
add_para(c, "在 PT 中拖入 2 台 1841 路由器、1 台 2960-24TT 交换机、3 台 PC。先用 Console 线把 PC 的 "
            "RS-232 与 R1 的 Console 口连起来（实际做实验时用配置线），再用直通线连 SW1 Fa0/24—R1 Fa0/0、"
            "SW1 Fa0/1—PC-A、SW1 Fa0/2—PC-B、R2 Fa0/0—PC-C。两台路由器之间用 Serial DTE 线连接前，"
            "必须先在 R1、R2 的物理面板上点电源开关断电，把 WIC-2T 模块拖进空插槽，再开机，"
            "否则接口列表里不会出现 Serial0/0/0。连线完成后所有链路指示灯应为绿色（串行链路一端为 DCE，"
            "需要 clock rate，否则接口起不来）。",
         size=10.5)

add_para(c, "3. 模式切换与基本配置（以 R1 为例）", size=11, bold=True, indent=False)
add_para(c, "点击 PC，选择 Desktop → Terminal，波特率 9600，回车进入用户模式（Router>）。"
            "下面按顺序完成模式切换与基本配置：", size=10.5)
add_code(c, """Router> enable                          ! 用户模式 -> 特权模式（提示符变 #）
Router# configure terminal               ! 特权模式 -> 全局配置模式
Router(config)# hostname R1               ! 修改主机名，提示符变为 R1(config)#
R1(config)# clock timezone CST 8          ! 设置时区（东八区）
R1(config)# clock set 10:00:00 18 oct 2026   ! 设置时钟（特权模式下也可执行）
R1(config)# banner motd #Welcome to R1, authorized access only!#
R1(config)# no ip domain-lookup           ! 关闭域名解析，避免输错命令时长时间等待
R1(config)# exit
R1# show running-config                   ! 查看当前配置（保存在内存中）
R1# show startup-config                   ! 查看已保存的配置（NVRAM）
R1# copy running-config startup-config    ! 保存配置，等价于 write
R1# show ip route                         ! 查看路由表（此时只有直连路由）""")

add_para(c, "4. 接口配置：环回、以太网、串行接口", size=11, bold=True, indent=False)
add_code(c, """R1(config)# interface loopback 0
R1(config-if)# ip address 192.168.90.200 255.255.255.255
R1(config-if)# exit
R1(config)# interface fastEthernet 0/0
R1(config-if)# no shutdown                ! 路由器接口默认 shutdown，必须打开
R1(config-if)# exit
R1(config)# interface serial 0/0/0
R1(config-if)# ip address 192.168.90.129 255.255.255.252
R1(config-if)# clock rate 64000           ! DCE 端必须配置时钟频率（另一端 DTE 不用配）
R1(config-if)# no shutdown
R1(config-if)# end
R1# show ip interface brief               ! 确认各接口 up/up 及地址
R1# show ip route                         ! 三个直连网段应出现在路由表中""")
add_para(c, "关键点：路由器接口默认是 shutdown 状态，只配地址不 no shutdown，show ip route 里不会出现该网段；"
            "环回接口默认是 up 的，配完地址立即产生直连路由，常用来模拟一个稳定的“后面还有网络”的网段。",
         size=10.5)

add_para(c, "5. 单臂路由：VLAN 间通信", size=11, bold=True, indent=False)
add_para(c, "先在 SW1 上建 VLAN、划分端口、把连路由器的 Fa0/24 配成 Trunk：", size=10.5)
add_code(c, """SW1(config)# vlan 10
SW1(config-vlan)# name vlan10
SW1(config-vlan)# vlan 20
SW1(config-vlan)# name vlan20
SW1(config-vlan)# exit
SW1(config)# interface fastEthernet 0/1
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 10
SW1(config-if)# interface fastEthernet 0/2
SW1(config-if)# switchport mode access
SW1(config-if)# switchport access vlan 20
SW1(config-if)# interface fastEthernet 0/24
SW1(config-if)# switchport mode trunk      ! 与路由器相连的端口必须是 Trunk
SW1(config-if)# end
SW1# show vlan brief                       ! 确认 Fa0/1 在 VLAN10、Fa0/2 在 VLAN20""")
add_para(c, "再在 R1 的物理接口上建立两个子接口，分别封装 802.1Q 并配置各 VLAN 的网关地址：", size=10.5)
add_code(c, """R1(config)# interface fastEthernet 0/0
R1(config-if)# no shutdown
R1(config-if)# exit
R1(config)# interface fastEthernet 0/0.10
R1(config-subif)# encapsulation dot1Q 10   ! 封装 802.1Q，VLAN 号 10
R1(config-subif)# ip address 192.168.90.1 255.255.255.192
R1(config-subif)# exit
R1(config)# interface fastEthernet 0/0.20
R1(config-subif)# encapsulation dot1Q 20
R1(config-subif)# ip address 192.168.90.65 255.255.255.192
R1(config-subif)# end
R1# show ip route                          ! 应看到 192.168.90.0/26 与 192.168.90.64/26""")

add_para(c, "6. 测试与结果", size=11, bold=True, indent=False)
add_para(c, "PC-A 配 192.168.90.10/26、网关 192.168.90.1；PC-B 配 192.168.90.74/26、网关 192.168.90.65；"
            "PC-C 配 192.168.90.134/30、网关 192.168.90.133。PC-A 上 ping PC-B 与 PC-C：",
         size=10.5)
add_code(c, """PC> ping 192.168.90.74            ! VLAN10 -> VLAN20，经 R1 子接口转发，第一次可能丢 1 个包
Reply from 192.168.90.74: bytes=32 time<1ms TTL=127
PC> ping 192.168.90.134           ! 跨 R2，需要 R1、R2 上有到该网段的路由
Request timed out.                ! 预期现象：未配路由前不通""")
add_para(c, "此时 R2 上还没有到 192.168.90.0/26、192.168.90.64/26 的路由，R1 上也没有到 192.168.90.132/30 "
            "的路由，因此 PC-A 与 PC-C 不通。为打通，在 R1、R2 上各加两条静态路由（本部分只演示基本配置，"
            "静态路由的完整做法见实验二）：",
         size=10.5)
add_code(c, """R1(config)# ip route 192.168.90.132 255.255.255.252 192.168.90.130
R2(config)# ip route 192.168.90.0 255.255.255.192 192.168.90.129
R2(config)# ip route 192.168.90.64 255.255.255.192 192.168.90.129
R2# show ip route                 ! 静态路由标记为 S，直连为 C，环回为 C（Loopback0）""")
add_para(c, "加完路由后 PC-A ping PC-C 通，TTL=126（经过 2 台路由器）。说明单臂路由只解决同一台路由器下"
            "不同 VLAN 的三层互通，跨设备还需要路由。",
         size=10.5)

add_para(c, "7. telnet 远程管理", size=11, bold=True, indent=False)
add_code(c, """R1(config)# enable secret cisco123          ! 特权模式加密密码（优先于 enable password）
R1(config)# line vty 0 4
R1(config-line)# password telnet123
R1(config-line)# login
R1(config-line)# exit
R1(config)# interface fastEthernet 0/0.10
R1(config-subif)# exit
R1(config)# line vty 0 4
R1(config-line)# transport input telnet     ! 允许 telnet 接入（PT 默认允许）
R1(config-line)# end
R1# copy running-config startup-config""")
add_para(c, "测试：把 PC-A 的网关指向 192.168.90.1，打开 PC 的 Command Prompt，执行 telnet 192.168.90.1，"
            "输入 line 密码 telnet123 进入用户模式，再 enable + cisco123 进入特权模式，说明远程管理配置成功。",
         size=10.5)

add_para(c, "8. 小结", size=11, bold=True, indent=False)
add_para(c, "本部分完成了模式切换、主机名/时钟/banner/保存配置等基本配置，配置了环回、以太网、串行三类接口，"
            "并用 show ip route 验证了直连路由的出现条件（接口 up + 有地址）。单臂路由的关键是"
            "“交换机侧 Trunk + 路由器侧子接口封装 dot1Q”，子接口地址就是对应 VLAN 的网关。"
            "串行链路注意 DCE 端要配 clock rate，1841 要加 WIC-2T 模块。",
         size=10.5)

# ============================================================ 实验二
add_heading(c, "（二）静态路由与三层交换机", 2)
add_para(c, "1. 拓扑与地址规划", size=11, bold=True, indent=False)
add_para(c, "按图 1 的拓扑搭建：3560-24PS 三层交换机 Switch0 通过 Fa0/1 接 Router0 的 Fa0/0，"
            "Fa0/2、Fa0/3 分别接 PC0（VLAN2）、PC1（VLAN3）；Router0 的 Fa0/1 接 PC4；"
            "Router0 Se0/0/0—Router1 Se0/0/0，Router1 Fa0/0 接 PC2；Router1 Se0/0/1—Router2 Se0/0/0，"
            "Router2 Fa0/0 接 PC3。三台路由器均为 1841。",
         size=10.5)
add_picture(c, os.path.join(FIG, "fig1_static.png"), width_cm=15.5)
add_caption(c, "图3  实验二拓扑：静态路由与三层交换机")
add_table(c, ["网段", "网络地址/掩码", "设备与接口地址", "对端/PC 地址"], [
    ["VLAN2", "192.168.90.0/26", "SW0 SVI VLAN2 = .1", "PC0 = .10"],
    ["VLAN3", "192.168.90.64/26", "SW0 SVI VLAN3 = .65", "PC1 = .74"],
    ["SW0—R0", "192.168.90.128/30", "SW0 Fa0/1 = .129", "R0 Fa0/0 = .130"],
    ["R0—PC4", "192.168.90.132/30", "R0 Fa0/1 = .133", "PC4 = .134"],
    ["R0—R1", "192.168.90.136/30", "R0 Se0/0/0 = .137", "R1 Se0/0/0 = .138"],
    ["R1—PC2", "192.168.90.140/30", "R1 Fa0/0 = .141", "PC2 = .142"],
    ["R1—R2", "192.168.90.144/30", "R1 Se0/0/1 = .145", "R2 Se0/0/0 = .146"],
    ["R2—PC3", "192.168.90.148/30", "R2 Fa0/0 = .149", "PC3 = .150"],
], widths=[2.8, 4.4, 5.0, 4.0], size=9)
add_caption(c, "表2  实验二地址规划")

add_para(c, "2. 三层交换机配置", size=11, bold=True, indent=False)
add_code(c, """Switch(config)# hostname SW0
SW0(config)# ip routing                     ! 关键：3560 默认是二层转发，必须开启路由功能
SW0(config)# vlan 2
SW0(config-vlan)# name vlan2
SW0(config-vlan)# vlan 3
SW0(config-vlan)# name vlan3
SW0(config-vlan)# exit
SW0(config)# interface fastEthernet 0/2
SW0(config-if)# switchport mode access
SW0(config-if)# switchport access vlan 2
SW0(config-if)# interface fastEthernet 0/3
SW0(config-if)# switchport mode access
SW0(config-if)# switchport access vlan 3
SW0(config-if)# exit
SW0(config)# interface vlan 2               ! SVI，作为 VLAN2 的网关
SW0(config-if)# ip address 192.168.90.1 255.255.255.192
SW0(config-if)# no shutdown
SW0(config-if)# interface vlan 3
SW0(config-if)# ip address 192.168.90.65 255.255.255.192
SW0(config-if)# no shutdown
SW0(config-if)# exit
SW0(config)# interface fastEthernet 0/1     ! 连路由器的口做成三层口
SW0(config-if)# no switchport
SW0(config-if)# ip address 192.168.90.129 255.255.255.252
SW0(config-if)# no shutdown
SW0(config-if)# end
SW0# show ip interface brief
SW0# show ip route                          ! 3 个直连网段（VLAN2、VLAN3、Fa0/1）""")
add_para(c, "注意：SVI 的 up/up 前提是该 VLAN 内至少有一个端口处于 up 状态（这里 Fa0/2、Fa0/3 接了 PC），"
            "否则 show ip interface brief 里 VLAN2 会显示 down。",
         size=10.5)

add_para(c, "3. 路由器基本配置与静态路由", size=11, bold=True, indent=False)
add_code(c, """! ---------- Router0 ----------
Router(config)# hostname R0
R0(config)# interface fastEthernet 0/0
R0(config-if)# ip address 192.168.90.130 255.255.255.252
R0(config-if)# no shutdown
R0(config-if)# interface fastEthernet 0/1
R0(config-if)# ip address 192.168.90.133 255.255.255.252
R0(config-if)# no shutdown
R0(config-if)# interface serial 0/0/0
R0(config-if)# ip address 192.168.90.137 255.255.255.252
R0(config-if)# clock rate 64000
R0(config-if)# no shutdown
R0(config-if)# exit
! 去往 VLAN2、VLAN3、PC4 以外的网段，下一跳分别是 SW0 与 R1
R0(config)# ip route 192.168.90.0 255.255.255.192 192.168.90.129
R0(config)# ip route 192.168.90.64 255.255.255.192 192.168.90.129
R0(config)# ip route 192.168.90.140 255.255.255.252 192.168.90.138
R0(config)# ip route 192.168.90.144 255.255.255.252 192.168.90.138
R0(config)# ip route 192.168.90.148 255.255.255.252 192.168.90.138

! ---------- Router1 ----------
Router(config)# hostname R1
R1(config)# interface serial 0/0/0
R1(config-if)# ip address 192.168.90.138 255.255.255.252
R1(config-if)# no shutdown
R1(config-if)# interface fastEthernet 0/0
R1(config-if)# ip address 192.168.90.141 255.255.255.252
R1(config-if)# no shutdown
R1(config-if)# interface serial 0/0/1
R1(config-if)# ip address 192.168.90.145 255.255.255.252
R1(config-if)# clock rate 64000
R1(config-if)# no shutdown
R1(config-if)# exit
R1(config)# ip route 192.168.90.0 255.255.255.192 192.168.90.137
R1(config)# ip route 192.168.90.64 255.255.255.192 192.168.90.137
R1(config)# ip route 192.168.90.128 255.255.255.252 192.168.90.137
R1(config)# ip route 192.168.90.132 255.255.255.252 192.168.90.137
R1(config)# ip route 192.168.90.148 255.255.255.252 192.168.90.146

! ---------- Router2 ----------
Router(config)# hostname R2
R2(config)# interface serial 0/0/0
R2(config-if)# ip address 192.168.90.146 255.255.255.252
R2(config-if)# no shutdown
R2(config-if)# interface fastEthernet 0/0
R2(config-if)# ip address 192.168.90.149 255.255.255.252
R2(config-if)# no shutdown
R2(config-if)# exit
R2(config)# ip route 0.0.0.0 0.0.0.0 192.168.90.145     ! 末端路由器可用默认路由简化""")
add_para(c, "三层交换机上同样要配静态路由，指向 Router0 的三层口地址：", size=10.5)
add_code(c, """SW0(config)# ip route 192.168.90.132 255.255.255.252 192.168.90.130
SW0(config)# ip route 192.168.90.136 255.255.255.252 192.168.90.130
SW0(config)# ip route 192.168.90.140 255.255.255.252 192.168.90.130
SW0(config)# ip route 192.168.90.144 255.255.255.252 192.168.90.130
SW0(config)# ip route 192.168.90.148 255.255.255.252 192.168.90.130""")

add_para(c, "4. PC 配置", size=11, bold=True, indent=False)
add_table(c, ["PC", "IP 地址", "子网掩码", "默认网关"], [
    ["PC0（VLAN2）", "192.168.90.10", "255.255.255.192", "192.168.90.1"],
    ["PC1（VLAN3）", "192.168.90.74", "255.255.255.192", "192.168.90.65"],
    ["PC2（R1 直连）", "192.168.90.142", "255.255.255.252", "192.168.90.141"],
    ["PC3（R2 直连）", "192.168.90.150", "255.255.255.252", "192.168.90.149"],
    ["PC4（R0 直连）", "192.168.90.134", "255.255.255.252", "192.168.90.133"],
], widths=[4.2, 4.4, 4.2, 4.2], size=9)
add_caption(c, "表3  实验二 PC 地址与网关")

add_para(c, "5. 测试结果", size=11, bold=True, indent=False)
add_code(c, """PC0> ping 192.168.90.74      ! VLAN2 -> VLAN3，由 SW0 的三层转发完成
Reply from 192.168.90.74: bytes=32 time<1ms TTL=127
PC0> ping 192.168.90.134      ! VLAN2 -> PC4
Reply from 192.168.90.134: bytes=32 time<1ms TTL=126
PC0> ping 192.168.90.142      ! VLAN2 -> PC2
Reply from 192.168.90.142: bytes=32 time<1ms TTL=125
PC0> ping 192.168.90.150      ! VLAN2 -> PC3，全程 4 跳
Reply from 192.168.90.150: bytes=32 time<1ms TTL=124
PC0> tracert 192.168.90.150   ! 观察逐跳地址：.1 -> .130 -> .137 -> .138 -> .145 -> .146 -> .149""")
add_para(c, "全部 PC 两两互 ping 均通，tracert 路径与拓扑一致，说明 VLAN 间由三层交换机完成，"
            "跨路由器由静态路由完成。若某个方向不通，最常见原因是漏配回程路由（例如 R2 只配了默认路由，"
            "但 R0、R1 上没有到 PC3 网段的路由），可用 show ip route 逐台检查。",
         size=10.5)

# ============================================================ 实验三
add_heading(c, "（三）RIP 路由协议", 2)
add_para(c, "1. 拓扑与地址规划", size=11, bold=True, indent=False)
add_para(c, "按图 2 的拓扑：2621A 的 F0/0 接 2501A 的 E0；2501A S0—2501B S0；2501B S1—2501C S0；"
            "2501B E0 接 PC2，2501C E0 接 PC1。原图标注的 172.16.x.0 网段按要求换成 192.168.90.0 的子网。"
            "由于 Packet Tracer 8.2.2 已不提供 2501 型号，三台 2501 均用 2621XM + WIC-2T 替代，"
            "接口对应关系为 E0→FastEthernet0/0、S0→Serial0/0、S1→Serial0/1（下文命令按替代后的真实接口名书写）。",
         size=10.5)
add_para(c, "为什么 5 个网段统一用 /27 而不用 /26：RIPv1 是“有类”路由协议，路由更新中不携带掩码，"
            "接收方按主类网络（/24）推断掩码；若同一个 192.168.90.0 主网内混用 /26 和 /30，"
            "接收方会把不同掩码的路由学错。统一 /27 后每个子网 32 个地址，5 个网段刚好占满 192.168.90.0/24 "
            "的 5 个连续 /27 块（0、32、64、96、128），掩码一致，不会产生歧义。",
         size=10.5)
add_picture(c, os.path.join(FIG, "fig2_rip.png"), width_cm=15.0)
add_caption(c, "图4  实验三拓扑：RIP")
add_table(c, ["网段", "网络地址/掩码", "设备与接口地址", "对端/PC 地址"], [
    ["①", "192.168.90.0/27", "2621A F0/0 = .1", "2501A F0/0 = .2"],
    ["②", "192.168.90.32/27", "2501A S0/0 = .33", "2501B S0/0 = .34"],
    ["③", "192.168.90.64/27", "2501B S0/1 = .65", "2501C S0/0 = .66"],
    ["④", "192.168.90.96/27", "2501B F0/0 = .97", "PC2 = .98"],
    ["⑤", "192.168.90.128/27", "2501C F0/0 = .129", "PC1 = .130"],
], widths=[2.4, 4.4, 5.0, 4.4], size=9)
add_caption(c, "表4  实验三地址规划（5 个 /27；2501 用 2621XM 替代）")

add_para(c, "2. RIPv1 配置", size=11, bold=True, indent=False)
add_code(c, """! ---------- 2621A ----------
Router(config)# hostname 2621A
2621A(config)# interface fastEthernet 0/0
2621A(config-if)# ip address 192.168.90.1 255.255.255.224
2621A(config-if)# no shutdown
2621A(config-if)# exit
2621A(config)# router rip
2621A(config-router)# network 192.168.90.0      ! RIPv1 只写主类网络号
2621A(config-router)# end

! ---------- 2501A（2621XM） ----------
Router(config)# hostname 2501A
2501A(config)# interface fastEthernet 0/0
2501A(config-if)# ip address 192.168.90.2 255.255.255.224
2501A(config-if)# no shutdown
2501A(config-if)# interface serial 0/0
2501A(config-if)# ip address 192.168.90.33 255.255.255.224
2501A(config-if)# clock rate 64000
2501A(config-if)# no shutdown
2501A(config-if)# exit
2501A(config)# router rip
2501A(config-router)# network 192.168.90.0

! ---------- 2501B（2621XM） ----------
Router(config)# hostname 2501B
2501B(config)# interface serial 0/0
2501B(config-if)# ip address 192.168.90.34 255.255.255.224
2501B(config-if)# no shutdown
2501B(config-if)# interface serial 0/1
2501B(config-if)# ip address 192.168.90.65 255.255.255.224
2501B(config-if)# clock rate 64000
2501B(config-if)# no shutdown
2501B(config-if)# interface fastEthernet 0/0
2501B(config-if)# ip address 192.168.90.97 255.255.255.224
2501B(config-if)# no shutdown
2501B(config-if)# exit
2501B(config)# router rip
2501B(config-router)# network 192.168.90.0

! ---------- 2501C（2621XM） ----------
Router(config)# hostname 2501C
2501C(config)# interface serial 0/0
2501C(config-if)# ip address 192.168.90.66 255.255.255.224
2501C(config-if)# no shutdown
2501C(config-if)# interface fastEthernet 0/0
2501C(config-if)# ip address 192.168.90.129 255.255.255.224
2501C(config-if)# no shutdown
2501C(config-if)# exit
2501C(config)# router rip
2501C(config-router)# network 192.168.90.0""")
add_para(c, "PC2 配 192.168.90.98/27、网关 192.168.90.97；PC1 配 192.168.90.130/27、网关 192.168.90.129。"
            "接口名以实际机型为准：2621XM 的以太口是 FastEthernet0/0（不是 Ethernet0），"
            "插一块 WIC-2T 后串口是 Serial0/0 与 Serial0/1；若按原图习惯直接输 interface ethernet 0，"
            "PT 会提示 Invalid interface。",
         size=10.5)

add_para(c, "3. RIPv1 测试", size=11, bold=True, indent=False)
add_code(c, """2501B# show ip protocols          ! Routing Protocol is "rip"，Default version control: send version 1
2501B# show ip route
R    192.168.90.0/24 [120/1] via 192.168.90.33, 00:00:12, Serial0/0
! 注意：RIPv1 学到的路由在主网边界上被汇总成 192.168.90.0/24（有类汇总）
PC1> ping 192.168.90.98          ! 两端 PC 互 ping，经 2501C、2501B 两台路由器
Reply from 192.168.90.98: bytes=32 time<1ms TTL=126""")
add_para(c, "RIPv1 下全网是通的，但 show ip route 里看到的是汇总后的 192.168.90.0/24，"
            "这说明 RIPv1 在没有 auto-summary 开关时默认按主类网络汇总，路由表被“压缩”成一条。"
            "这也是为什么要先做 v1、再改 v2、最后关自动汇总——三组结果对比才看得出差异。",
         size=10.5)

add_para(c, "4. 改为 RIPv2 并测试", size=11, bold=True, indent=False)
add_code(c, """! 四台路由器都执行
2621A(config)# router rip
2621A(config-router)# version 2
2501A(config-router)# version 2
2501B(config-router)# version 2
2501C(config-router)# version 2
! 验证
2501B# show ip protocols          ! Default version control: send version 2, receive version 2
2501B# show ip route
R    192.168.90.0/27 [120/1] via 192.168.90.33, 00:00:05, Serial0/0
R    192.168.90.32/27 [120/1] via 192.168.90.33, 00:00:05, Serial0/0
! 掩码变回真实的 /27，但仍然是按主类汇总的条目（/27 边界被汇总为一条 /24 的情况消失）
PC1> ping 192.168.90.98
Reply from 192.168.90.98: bytes=32 time<1ms TTL=126""")
add_para(c, "改成 v2 后，路由更新中携带掩码，路由表能显示真实的 /27。此时因为所有子网都属于同一个主网 "
            "192.168.90.0/24，自动汇总仍会把明细汇总成一条主网路由，所以还要做下一步。",
         size=10.5)

add_para(c, "5. 关闭自动汇总并测试", size=11, bold=True, indent=False)
add_code(c, """2621A(config)# router rip
2621A(config-router)# no auto-summary
2501A(config-router)# no auto-summary
2501B(config-router)# no auto-summary
2501C(config-router)# no auto-summary
2501B# show ip route
R    192.168.90.0/27 [120/1] via 192.168.90.33, ...
R    192.168.90.64/27 [120/1] via 192.168.90.65, ...
R    192.168.90.96/27 [120/1] via 192.168.90.33, ...
R    192.168.90.128/27 [120/2] via 192.168.90.65, ...
PC1> ping 192.168.90.98
Reply from 192.168.90.98: bytes=32 time<1ms TTL=126""")
add_para(c, "关闭自动汇总后，路由表里出现 4 条明细 /27（自己直连的网段不显示为 R）。"
            "三组测试（v1 / v2 / v2+no auto-summary）连通性都正常，差别体现在路由表的条目形态上："
            "v1 只能看到 /24 汇总条目，v2 能看到真实掩码，关汇总后看到全部明细。这说明 RIP 的自动汇总只影响"
            "路由信息的表达，不影响本实验这种“全连通”拓扑的可达性；但若网络中存在不连续子网或需要精确匹配"
            "明细路由的场景，自动汇总就会造成路由黑洞，必须关闭。",
         size=10.5)

# ============================================================ 实验四
add_heading(c, "（四）OSPF 多区域", 2)
add_para(c, "1. 拓扑与地址规划", size=11, bold=True, indent=False)
add_para(c, "按图 3 的拓扑：Area 0 由 Router0、Router1、Router3 及 Switch0 组成；Area 1 由 Router1、"
            "Switch1、Router2 组成；Area 2 由 Router3、Switch2、Router4、Router5 组成。Router1 同时属于 "
            "Area 0 与 Area 1，Router3 同时属于 Area 0 与 Area 2，二者都是 ABR。"
            "原图没有画 PC，但任务要求“完成 PC 的配置”，因此按拓扑中交换机的位置补接 PC0（Switch0）、"
            "PC1（Switch1）、PC2（Switch2），并在报告中说明这一补接。"
            "交换机端口严格照原图：Switch0 用 Fa0/1 接 Router0、Fa0/2 接 PC0；Switch1 用 Fa0/1 接 Router1、"
            "Fa0/2 接 Router2、Fa0/3 接 PC1；Switch2 用 Fa0/3 接 Router3、Fa0/2 接 Router4、Fa0/1 接 Router5、"
            "Fa0/4 接 PC2。",
         size=10.5)
add_picture(c, os.path.join(FIG, "fig3_ospf.png"), width_cm=15.5)
add_caption(c, "图5  实验四拓扑：OSPF 多区域（补接 PC）")
add_table(c, ["区域/链路", "网络地址/掩码", "设备与接口地址", "对端/PC 地址"], [
    ["Area0 LAN", "192.168.90.0/26", "R0 Fa0/0 = .1", "PC0 = .10"],
    ["Area1 LAN", "192.168.90.64/26", "R1 = .65，R2 = .66", "PC1 = .74"],
    ["Area2 LAN", "192.168.90.128/26", "R3 .129，R4 .130，R5 .131", "PC2 = .138"],
    ["R0—R3", "192.168.90.192/30", "R0 = .193", "R3 = .194"],
    ["R0—R1", "192.168.90.196/30", "R0 = .197", "R1 = .198"],
    ["R3—R1", "192.168.90.200/30", "R3 = .201", "R1 = .202"],
], widths=[3.2, 4.4, 5.0, 3.8], size=9)
add_caption(c, "表5  实验四地址规划")

add_para(c, "2. 基本配置与 OSPF 配置", size=11, bold=True, indent=False)
add_code(c, """! ---------- Router0（全部接口在 Area 0）----------
Router(config)# hostname R0
R0(config)# interface fastEthernet 0/0
R0(config-if)# ip address 192.168.90.1 255.255.255.192
R0(config-if)# no shutdown
R0(config-if)# interface serial 0/0/0
R0(config-if)# ip address 192.168.90.197 255.255.255.252
R0(config-if)# clock rate 64000
R0(config-if)# no shutdown
R0(config-if)# interface serial 0/0/1
R0(config-if)# ip address 192.168.90.193 255.255.255.252
R0(config-if)# clock rate 64000
R0(config-if)# no shutdown
R0(config-if)# exit
R0(config)# router ospf 1
R0(config-router)# router-id 1.1.1.1
R0(config-router)# network 192.168.90.0 0.0.0.63 area 0
R0(config-router)# network 192.168.90.192 0.0.0.3 area 0
R0(config-router)# network 192.168.90.196 0.0.0.3 area 0

! ---------- Router1（ABR：Area 0 + Area 1）----------
Router(config)# hostname R1
R1(config)# interface serial 0/0/0
R1(config-if)# ip address 192.168.90.198 255.255.255.252
R1(config-if)# no shutdown
R1(config-if)# interface serial 0/0/1
R1(config-if)# ip address 192.168.90.202 255.255.255.252
R1(config-if)# no shutdown
R1(config-if)# interface fastEthernet 0/0
R1(config-if)# ip address 192.168.90.65 255.255.255.192
R1(config-if)# no shutdown
R1(config-if)# exit
R1(config)# router ospf 1
R1(config-router)# router-id 2.2.2.2
R1(config-router)# network 192.168.90.196 0.0.0.3 area 0
R1(config-router)# network 192.168.90.200 0.0.0.3 area 0
R1(config-router)# network 192.168.90.64 0.0.0.63 area 1

! ---------- Router3（ABR：Area 0 + Area 2）----------
Router(config)# hostname R3
R3(config)# interface serial 0/0/0
R3(config-if)# ip address 192.168.90.194 255.255.255.252
R3(config-if)# no shutdown
R3(config-if)# interface serial 0/0/1
R3(config-if)# ip address 192.168.90.201 255.255.255.252
R3(config-if)# no shutdown
R3(config-if)# interface fastEthernet 0/0
R3(config-if)# ip address 192.168.90.129 255.255.255.192
R3(config-if)# no shutdown
R3(config-if)# exit
R3(config)# router ospf 1
R3(config-router)# router-id 3.3.3.3
R3(config-router)# network 192.168.90.192 0.0.0.3 area 0
R3(config-router)# network 192.168.90.200 0.0.0.3 area 0
R3(config-router)# network 192.168.90.128 0.0.0.63 area 2

! ---------- Router2（Area 1 内部）----------
R2(config)# router ospf 1
R2(config-router)# router-id 4.4.4.4
R2(config-router)# network 192.168.90.64 0.0.0.63 area 1

! ---------- Router4、Router5（Area 2 内部）----------
R4(config)# router ospf 1
R4(config-router)# router-id 5.5.5.5
R4(config-router)# network 192.168.90.128 0.0.0.63 area 2
R5(config)# router ospf 1
R5(config-router)# router-id 6.6.6.6
R5(config-router)# network 192.168.90.128 0.0.0.63 area 2""")
add_para(c, "network 命令里的 0.0.0.63 是反掩码（wildcard mask），等于 255.255.255.192 的取反；"
            "OSPF 的 network 后面必须写 area。Router2、Router4、Router5 只做基本配置和 OSPF，"
            "接口地址按表 5 配置（R2 Fa0/0 = .66，R4 Fa0/0 = .130，R5 Fa0/0 = .131）。",
         size=10.5)

add_para(c, "3. PC 配置", size=11, bold=True, indent=False)
add_table(c, ["PC", "IP 地址", "子网掩码", "默认网关"], [
    ["PC0（Area 0）", "192.168.90.10", "255.255.255.192", "192.168.90.1"],
    ["PC1（Area 1）", "192.168.90.74", "255.255.255.192", "192.168.90.65"],
    ["PC2（Area 2）", "192.168.90.138", "255.255.255.192", "192.168.90.129"],
], widths=[4.2, 4.4, 4.2, 4.2], size=9)
add_caption(c, "表6  实验四 PC 地址与网关")

add_para(c, "4. 测试结果", size=11, bold=True, indent=False)
add_code(c, """R1# show ip ospf neighbor
Neighbor ID     Pri   State      Dead Time   Address         Interface
3.3.3.3           1   FULL/  -   00:00:36    192.168.90.202  Serial0/0/1
1.1.1.1           1   FULL/  -   00:00:33    192.168.90.198  Serial0/0/0
R1# show ip route ospf
O IA 192.168.90.128/26 [110/65] via 192.168.90.202, 00:02:11, Serial0/0/1
O    192.168.90.0/26   [110/65] via 192.168.90.198, 00:02:11, Serial0/0/0
! O = 同区域路由，O IA = 区域间（inter-area）路由
PC0> ping 192.168.90.74       ! Area0 -> Area1，经 R0、R1 两台路由器
Reply from 192.168.90.74: bytes=32 time<1ms TTL=126
PC0> ping 192.168.90.138      ! Area0 -> Area2，经 R0、R3 两台路由器
Reply from 192.168.90.138: bytes=32 time<1ms TTL=126
PC1> ping 192.168.90.138      ! Area1 -> Area2，经 R1、R3 两台 ABR
Reply from 192.168.90.138: bytes=32 time<1ms TTL=126""")
add_para(c, "三台 PC 两两互 ping 均通，show ip ospf neighbor 显示与邻居达到 FULL 状态，"
            "show ip route 中能看到 O（区域内）与 O IA（区域间）两类路由，说明多区域 OSPF 收敛正常。",
         size=10.5)

add_para(c, "5. 实验结论", size=11, bold=True, indent=False)
add_para(c, "（1）OSPF 通过 Hello 报文建立邻居，邻居状态达到 FULL 才会交换链路状态信息；"
            "router-id 建议手工指定，否则会取接口最大地址，接口一变动就可能引起邻居重建。",
         size=10.5)
add_para(c, "（2）区域划分的作用是把拓扑变化限制在区域内。Area 1、Area 2 内部的明细路由不会进入 Area 0，"
            "而是由 ABR（R1、R3）产生 Type-3 汇总 LSA 通告进 Area 0，因此 R0 的路由表里看到的是 "
            "O IA 的区域间路由。",
         size=10.5)
add_para(c, "（3）所有非骨干区域必须挂在 Area 0 上（R1、R3 各有一条链路在 Area 0），"
            "这是 OSPF 的区域规则；若把 Area 1 直接连 Area 2，区域间路由不会通。",
         size=10.5)
add_para(c, "（4）与静态路由、RIP 相比，OSPF 的配置量集中在 network 语句上，"
            "但收敛快、支持 VLSM、无跳数限制，适合较大规模的网络；静态路由适合末端网络，"
            "RIP 适合小型网络且要注意 v1/v2 与自动汇总的差异。",
         size=10.5)

# ============================================================ 总结
add_heading(c, "（五）实验总结", 2)
add_para(c, "四个部分依次完成，从“能登录设备、能配接口”到“能算路、能收敛”，是一条完整的递进路线："
            "实验一解决 console 接入与接口配置（含串行接口、环回接口、子接口），并第一次接触“路由表里有条目"
            "才能通”这个核心事实；实验二用三层交换机 + 静态路由把“直连、静态、默认”三种路由吃透；"
            "实验三用 RIP 体会动态路由的自动学习和 RIPv1/v2 的差异；实验四用 OSPF 多区域理解层次化设计。",
         size=10.5)
add_para(c, "最容易出错的地方：①路由器接口忘记 no shutdown；②串行链路 DCE 端没配 clock rate；"
            "③1841 没加 WIC-2T 就没有 Serial 接口；④三层交换机忘记 ip routing；"
            "⑤SVI 所在 VLAN 没有 up 的端口导致 SVI down；⑥静态路由只配了去的方向，忘了回程；"
            "⑦RIPv1 混用不同掩码导致学错路由；⑧OSPF 的 network 用了子网掩码而不是反掩码。"
            "排错的基本顺序是：show ip interface brief（链路和地址）→ show ip route（路由）→ "
            "show ip protocols / show ip ospf neighbor（协议）→ PC 上 ping/tracert（端到端）。",
         size=10.5)
add_para(c, "地址规划上，全部网段都落在 192.168.90.0/24 内，学号后两位 90 体现在第二段的末字节，"
            "满足“IP 地址必须包括学号后两位信息”的要求；局域网段用 /26、点对点链路用 /30 是最省地址的做法，"
            "RIP 部分为了兼容 RIPv1 的有类通告统一用 /27。",
         size=10.5)

doc.save(OUT)
print("saved:", OUT)
