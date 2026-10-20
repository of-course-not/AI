# -*- coding: utf-8 -*-
"""用 donor 设备 XML + 6.1 骨架拼装 Packet Tracer 工程文件。"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DON = os.path.join(HERE, "_donors")
BASE = os.path.join(HERE, "_base61.xml")

MAC_SEQ = [0]


def _mac():
    MAC_SEQ[0] += 1
    n = MAC_SEQ[0]
    return "0000.0C%02X.%04X" % ((n >> 16) & 0xFF, n & 0xFFFF)


def _ipv6_ll(mac):
    """由 MAC 生成 EUI-64 链路本地地址（PT 的写法）。"""
    h = mac.replace(".", "")
    b = [int(h[i:i + 2], 16) for i in range(0, 12, 2)]
    b[0] ^= 0x02
    mid = [b[0], b[1], b[2], 0xFF, 0xFE, b[3], b[4], b[5]]
    return "FE80::" + ":".join("%02X%02X" % (mid[i], mid[i + 1])
                               for i in range(0, 8, 2))


def _block(text, tag):
    i = text.find("<%s>" % tag)
    if i < 0:
        i = text.find("<%s " % tag)
    j = text.find("</%s>" % tag, i)
    return text[i:j + len(tag) + 3]


# ---------------------------------------------------------------- 设备模板

def donor_device(kind):
    """返回 donor 的 <DEVICE>…</DEVICE> 原文。"""
    x = open(os.path.join(DON, kind + ".xml"), encoding="utf-8").read()
    return _block(x, "DEVICE")


def _hwic_slot(model="WIC-2T"):
    """从 1841 donor 里取出插了 HWIC-2T 的 SLOT 片段，改型号。"""
    x = donor_device("1841")
    m = re.search(r"<SLOT>\s*<TYPE>eInterfaceCard</TYPE>\s*<MODULE>(?:(?!</SLOT>).)*?"
                  r"<MODEL>HWIC-2T</MODEL>.*?</MODULE>\s*</SLOT>", x, re.S)
    slot = m.group(0)
    return slot.replace("HWIC-2T", model)


def with_wic2t(block, model="WIC-2T"):
    """把 2621XM 的空 WIC 槽替换成插了 WIC-2T 的槽（前 n 个空槽）。"""
    empty = "<SLOT>\n         <TYPE>eInterfaceCard</TYPE>\n        </SLOT>"
    slot = _hwic_slot(model)
    slot = re.sub(r"\n\s*", "\n         ", slot).strip()
    cnt = block.count(empty)
    if cnt == 0:
        # 缩进可能不同，用正则兜底
        pat = re.compile(r"<SLOT>\s*<TYPE>eInterfaceCard</TYPE>\s*</SLOT>")
        cnt = len(pat.findall(block))
        return pat.sub(lambda m: slot, block), cnt
    return block.replace(empty, slot), cnt


PORT_NAMES = {
    "1841": ["Serial0/0/0", "Serial0/0/1", "FastEthernet0/0", "FastEthernet0/1"],
    "2621XM": ["Serial0/0/0", "Serial0/0/1", "Serial0/1/0", "Serial0/1/1",
               "FastEthernet0/0", "FastEthernet0/1"],
    "PC-PT": ["FastEthernet0"],
}

SWITCH_PORTS = {}
for _n in (24,):
    SWITCH_PORTS["2950-24"] = ["FastEthernet0/%d" % i for i in range(1, 25)]
    SWITCH_PORTS["2960-24TT"] = (["FastEthernet0/%d" % i for i in range(1, 25)]
                                + ["GigabitEthernet0/1", "GigabitEthernet0/2"])
    SWITCH_PORTS["3560-24PS"] = (["FastEthernet0/%d" % i for i in range(1, 25)]
                                 + ["GigabitEthernet0/1", "GigabitEthernet0/2"])


def port_names(kind, block):
    if kind == "2621XM":
        # 每张 WIC-2T 提供 2 个串口，命名连续：Serial0/0、Serial0/1、Serial0/2、Serial0/3
        n = block.count("<MODEL>WIC-2T</MODEL>")
        return (["Serial0/%d" % i for i in range(2 * n)]
                + ["FastEthernet0/0", "FastEthernet0/1"])
    if kind in PORT_NAMES:
        return PORT_NAMES[kind]
    return SWITCH_PORTS[kind]


def set_ports(block, kind, cfg):
    """cfg: {portname: (ip, mask, power)}；返回新块。"""
    names = port_names(kind, block)
    out = []
    idx = 0
    pos = 0
    while True:
        i = block.find("<PORT>", pos)
        if i < 0:
            out.append(block[pos:])
            break
        j = block.find("</PORT>", i) + len("</PORT>")
        out.append(block[pos:i])
        seg = block[i:j]
        if idx < len(names):
            name = names[idx]
            ip, mask, power = cfg.get(name, ("", "", False))
            seg = re.sub(r"<POWER>[^<]*</POWER>",
                         "<POWER>%s</POWER>" % ("true" if power else "false"), seg, 1)
            seg = re.sub(r"<IP/>|<IP>[^<]*</IP>", "<IP>%s</IP>" % ip if ip else "<IP/>", seg, 1)
            seg = re.sub(r"<SUBNET/>|<SUBNET>[^<]*</SUBNET>",
                         "<SUBNET>%s</SUBNET>" % mask if mask else "<SUBNET/>", seg, 1)
            mac = _mac()
            seg = re.sub(r"<MACADDRESS>[^<]*</MACADDRESS>",
                         "<MACADDRESS>%s</MACADDRESS>" % mac, seg, 1)
            seg = re.sub(r"<BIA>[^<]*</BIA>", "<BIA>%s</BIA>" % mac, seg, 1)
            seg = re.sub(r"<IPV6_DEFAULT_LINK_LOCAL>[^<]*</IPV6_DEFAULT_LINK_LOCAL>",
                         "<IPV6_DEFAULT_LINK_LOCAL>%s</IPV6_DEFAULT_LINK_LOCAL>"
                         % _ipv6_ll(mac), seg, 1)
        out.append(seg)
        pos = j
        idx += 1
    return "".join(out)


def set_running(block, lines):
    body = "".join("<LINE>%s</LINE>" % l for l in lines)
    return re.sub(r"<RUNNINGCONFIG>.*?</RUNNINGCONFIG>",
                  "<RUNNINGCONFIG>%s</RUNNINGCONFIG>" % body, block, flags=re.S)


def set_vlans(block, vlans):
    """vlans: [(id, name)] 追加到 VLANS 里。"""
    add = "".join('<VLAN number="%d" name="%s"/>' % v for v in vlans)
    return block.replace("</VLANS>", add + "</VLANS>", 1)


def rename(block, name, x, y, mem):
    block = re.sub(r'(<NAME[^>]*>)[^<]*(</NAME>)', r"\g<1>%s\g<2>" % name, block, 1)
    block = re.sub(r"<SYS_NAME>[^<]*</SYS_NAME>",
                   "<SYS_NAME>%s</SYS_NAME>" % name, block, 1)
    block = re.sub(r"<X>[^<]*</X>", "<X>%s</X>" % x, block, 1)
    block = re.sub(r"<Y>[^<]*</Y>", "<Y>%s</Y>" % y, block, 1)
    block = re.sub(r"<MEM_ADDR>[^<]*</MEM_ADDR>",
                   "<MEM_ADDR>%d</MEM_ADDR>" % mem, block, 1)
    block = re.sub(r"<DEV_ADDR>[^<]*</DEV_ADDR>",
                   "<DEV_ADDR>%d</DEV_ADDR>" % (mem + 1000), block, 1)
    block = re.sub(r'<PHYSICAL translate="true">[^<]*</PHYSICAL>',
                   '<PHYSICAL translate="true">Intercity,Home City,Corporate Office,'
                   'Main Wiring Closet,Rack,%s</PHYSICAL>' % name, block, 1)
    block = re.sub(r"<X_COORD>[^<]*</X_COORD>", "<X_COORD>%s</X_COORD>" % x, block, 1)
    block = re.sub(r"<Y_COORD>[^<]*</Y_COORD>", "<Y_COORD>%s</Y_COORD>" % y, block, 1)
    return block


def set_clock(block, kind, dce_ports, rate=64000):
    """把 DCE 端串口的 CLOCKRATE 设为 rate、CLOCKRATEFLAG 设为 true。"""
    names = port_names(kind, block)
    out = []
    pos = 0
    idx = 0
    while True:
        i = block.find("<PORT>", pos)
        if i < 0:
            out.append(block[pos:])
            break
        j = block.find("</PORT>", i) + len("</PORT>")
        out.append(block[pos:i])
        seg = block[i:j]
        if idx < len(names) and names[idx] in dce_ports:
            seg = re.sub(r"<CLOCKRATE>[^<]*</CLOCKRATE>",
                         "<CLOCKRATE>%d</CLOCKRATE>" % rate, seg, 1)
            seg = re.sub(r"<CLOCKRATEFLAG>[^<]*</CLOCKRATEFLAG>",
                         "<CLOCKRATEFLAG>true</CLOCKRATEFLAG>", seg, 1)
        out.append(seg)
        pos = j
        idx += 1
    return "".join(out)


# ---------------------------------------------------------------- 组装

def make_link(idx_a, port_a, idx_b, port_b, kind="eCopper", cable="eStraightThrough",
              dce=None, mem=900000000):
    if kind == "eSerial":
        body = ("<LINK><TYPE>eSerial</TYPE><CABLE>"
                "<LENGTH>0</LENGTH>"
                "<FROM>%d</FROM><PORT>%s</PORT>"
                "<TO>%d</TO><PORT>%s</PORT>"
                "<FROM_DEVICE_MEM_ADDR>%d</FROM_DEVICE_MEM_ADDR>"
                "<TO_DEVICE_MEM_ADDR>%d</TO_DEVICE_MEM_ADDR>"
                "<FROM_PORT_MEM_ADDR>%d</FROM_PORT_MEM_ADDR>"
                "<TO_PORT_MEM_ADDR>%d</TO_PORT_MEM_ADDR>"
                "<DCEDEV>%d</DCEDEV><DCEPORT>%s</DCEPORT>"
                "</CABLE></LINK>"
                % (idx_a, port_a, idx_b, port_b, mem, mem + 1, mem + 2, mem + 3,
                   dce if dce is not None else idx_a,
                   port_a if dce is None else (port_b if dce == idx_b else port_a)))
    else:
        body = ("<LINK><TYPE>eCopper</TYPE><CABLE>"
                "<LENGTH>1</LENGTH>"
                "<FROM>%d</FROM><PORT>%s</PORT>"
                "<TO>%d</TO><PORT>%s</PORT>"
                "<FROM_DEVICE_MEM_ADDR>%d</FROM_DEVICE_MEM_ADDR>"
                "<TO_DEVICE_MEM_ADDR>%d</TO_DEVICE_MEM_ADDR>"
                "<FROM_PORT_MEM_ADDR>%d</FROM_PORT_MEM_ADDR>"
                "<TO_PORT_MEM_ADDR>%d</TO_PORT_MEM_ADDR>"
                "<GEO_VIEW_COLOR>#000000</GEO_VIEW_COLOR>"
                "<TYPE>%s</TYPE>"
                "</CABLE></LINK>"
                % (idx_a, port_a, idx_b, port_b, mem, mem + 1, mem + 2, mem + 3, cable))
    return body


def build(devices, links, notes=None):
    """devices: [device_block…]；links: [link_xml…]。"""
    base = open(BASE, encoding="utf-8").read()
    devs = "<DEVICES>\n   " + "\n   ".join(devices) + "\n  </DEVICES>"
    lnks = "<LINKS>\n   " + "\n   ".join(links) + "\n  </LINKS>"
    base = re.sub(r"<DEVICES>.*?</DEVICES>", lambda m: devs, base, count=1, flags=re.S)
    base = re.sub(r"<LINKS>.*?</LINKS>", lambda m: lnks, base, count=1, flags=re.S)
    base = re.sub(r'<DESCRIPTION translate="true">[^<]*</DESCRIPTION>',
                  '<DESCRIPTION translate="true"></DESCRIPTION>', base, count=1)
    # 机架里的设备 NODE：按设备名重建
    names = [re.search(r'<NAME[^>]*>([^<]*)</NAME>', d).group(1) for d in devices]
    nodes = []
    for i, n in enumerate(names):
        nodes.append(
            "<NODE><X>%d</X><Y>0</Y><TYPE>6</TYPE>"
            '<NAME translate="true">%s</NAME><SX>1</SX><SY>1</SY><W>0</W><H>0</H>'
            "<PATH>../art/Background/grid_100x100.png</PATH><CHILDREN/>"
            "<MANUAL_SCALING>false</MANUAL_SCALING>"
            "<SCALED_PIXMAP_WIDTH>0</SCALED_PIXMAP_WIDTH>"
            "<SCALED_PIXMAP_HEIGHT>0</SCALED_PIXMAP_HEIGHT>"
            "<INIT_WIDTH>0</INIT_WIDTH><INIT_HEIGHT>0</INIT_HEIGHT>"
            "<INIT_SX>1</INIT_SX><INIT_SY>0</INIT_SY><BG_TILED>false</BG_TILED></NODE>"
            % (5 + i * 8, n))
    i = base.find("<TYPE>4</TYPE>")
    j = base.find("<CHILDREN>", i)
    k = base.find("</CHILDREN>", j)
    base = base[:j] + "<CHILDREN>" + "".join(nodes) + base[k:]
    # 注释框
    nb = []
    for n_i, (nx, ny, txt) in enumerate(notes or []):
        nb.append('<NOTE uuid="{aaaaaaaa-0000-4000-8000-%012d}"><X>%d</X><Y>%d</Y>'
                  "<Z>%d</Z>"
                  '<TEXT translate="true">%s</TEXT>'
                  "<NOTECLUSTERID>1-1</NOTECLUSTERID></NOTE>"
                  % (n_i + 1, nx, ny, 40000 + n_i * 2, txt))
    base = re.sub(r"<NOTES>.*?</NOTES>", "<NOTES>" + "".join(nb) + "</NOTES>",
                  base, count=1, flags=re.S)
    return base
