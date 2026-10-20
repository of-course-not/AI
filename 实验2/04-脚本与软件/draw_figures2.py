# -*- coding: utf-8 -*-
"""实验二（ACL / NAT）拓扑图绘制。

布局规则与实验一相同：设备 + 接口名在上，地址全部集中到底部表格，
这样图里不会有图例框压住设备，打印/缩放都不会糊。
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

OUT = r"E:\Deepseek\DSH-Demo-Har\NetRouter\实验2\06-图表与截图"
os.makedirs(OUT, exist_ok=True)

CJK_PATH = r"C:\Windows\Fonts\simhei.ttf"
MONO_PATH = r"C:\Windows\Fonts\consola.ttf"

BG = (255, 255, 255)
LINE = (45, 45, 45)
SER = (192, 45, 45)
ROUTER_FILL = (220, 234, 248)
SWITCH_FILL = (226, 240, 217)
PC_FILL = (252, 238, 218)
SRV_FILL = (240, 228, 245)
NET = (22, 62, 140)
WARN = (150, 32, 32)
OK = (20, 96, 45)
GREY = (95, 95, 95)
GRID = (205, 210, 220)
HEAD_FILL = (233, 238, 246)


def _has_cjk(text):
    return any(ord(ch) > 127 for ch in text)


def font(size, text=""):
    return ImageFont.truetype(CJK_PATH if _has_cjk(text) else MONO_PATH, size)


def device(d, xy, label, sub, fill, kind="router", w=104, h=56, label_above=False,
           label_side=None):
    x, y = xy
    d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=fill, outline=LINE, width=2)
    cx, cy = x + w / 2, y + h / 2
    if kind == "router":
        d.line([x + 16, cy - 7, x + w - 16, cy - 7], fill=LINE, width=1)
        d.line([x + 16, cy + 7, x + w - 16, cy + 7], fill=LINE, width=1)
        d.line([cx, cy - 12, cx, cy + 12], fill=LINE, width=1)
        d.ellipse([cx - 3, cy - 17, cx + 3, cy - 11], fill=LINE)
    elif kind == "switch":
        for i in range(4):
            xx = x + 15 + i * (w - 30) / 4
            d.rectangle([xx, cy - 5, xx + 11, cy + 5], fill=LINE)
    elif kind == "server":
        d.rectangle([cx - 13, y + 9, cx + 13, y + h - 7], fill=LINE)
        for i in range(3):
            d.rectangle([cx - 9, y + 14 + i * 10, cx + 9, y + 20 + i * 10], fill=BG)
    else:
        d.rectangle([cx - 14, y + 9, cx + 14, y + h - 15], fill=LINE)
        d.rectangle([cx - 20, y + h - 15, cx + 20, y + h - 7], fill=LINE)
    if label_side == "left":
        d.text((x - 10, cy - 9), label, font=font(15, label), fill=(12, 12, 12), anchor="rm")
        if sub:
            d.text((x - 10, cy + 11), sub, font=font(12, sub), fill=GREY, anchor="rm")
    elif label_side == "right":
        d.text((x + w + 10, cy - 9), label, font=font(15, label), fill=(12, 12, 12), anchor="lm")
        if sub:
            d.text((x + w + 10, cy + 11), sub, font=font(12, sub), fill=GREY, anchor="lm")
    elif label_above:
        d.text((cx, y - 24), label, font=font(15, label), fill=(12, 12, 12), anchor="ma")
        if sub:
            d.text((cx, y - 44), sub, font=font(12, sub), fill=GREY, anchor="ma")
    else:
        d.text((cx, y + h + 6), label, font=font(15, label), fill=(12, 12, 12), anchor="ma")
        if sub:
            d.text((cx, y + h + 25), sub, font=font(12, sub), fill=GREY, anchor="ma")
    return (cx, cy)


def link(d, p1, p2, color=LINE, width=2, dashed=False):
    if not dashed:
        d.line([p1, p2], fill=color, width=width)
        return
    x1, y1 = p1
    x2, y2 = p2
    dist = math.hypot(x2 - x1, y2 - y1)
    steps = max(2, int(dist / 10))
    for i in range(steps):
        if i % 2 == 0:
            a, b = i / steps, min(1.0, (i + 0.55) / steps)
            d.line([(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a),
                    (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)], fill=color, width=width)


def iface(d, p1, p2, text, frac=0.5, off=14, color=WARN, size=11):
    x1, y1 = p1
    x2, y2 = p2
    mx, my = x1 + (x2 - x1) * frac, y1 + (y2 - y1) * frac
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1
    px, py = -dy / length, dx / length
    cx, cy = mx + px * off, my + py * off
    f = font(size, text)
    tw = d.textlength(text, font=f)
    d.rectangle([cx - tw / 2 - 3, cy - 8, cx + tw / 2 + 3, cy + 8], fill=BG)
    d.text((cx, cy), text, font=f, fill=color, anchor="mm")


def note(d, xy, lines, color=NET, size=11, anchor="lm", gap=6):
    x, y = xy
    for i, text in enumerate(lines):
        d.text((x, y + i * (size + gap)), text, font=font(size, text), fill=color, anchor=anchor)


def table(d, xy, rows, widths, size=11, rh=24):
    x, y = xy
    total = sum(widths)
    h = rh * (len(rows) + 1)
    d.rectangle([x, y, x + total, y + h], fill=(250, 251, 253), outline=GRID, width=1)
    d.rectangle([x, y, x + total, y + rh], fill=HEAD_FILL, outline=GRID, width=1)
    header = ["网段", "网络地址 / 掩码", "设备与接口地址", "对端 / PC 地址"]
    cx = x
    for i, w in enumerate(widths):
        if i:
            d.line([cx, y, cx, y + h], fill=GRID, width=1)
        d.text((cx + 7, y + rh / 2), header[i], font=font(size, header[i]),
               fill=(40, 46, 58), anchor="lm")
        cx += w
    for r, row in enumerate(rows):
        ry = y + rh * (r + 1)
        d.line([x, ry, x + total, ry], fill=GRID, width=1)
        cx = x
        for i, cell in enumerate(row):
            d.text((cx + 7, ry + rh / 2), cell, font=font(size, cell),
                   fill=NET if i else (35, 35, 35), anchor="lm")
            cx += widths[i]


def title(d, main, sub=None):
    d.text((26, 18), main, font=font(20, main), fill=(10, 10, 10))
    if sub:
        d.text((26, 50), sub, font=font(13, sub), fill=GREY)


def canvas(w, h):
    im = Image.new("RGB", (w, h), BG)
    return im, ImageDraw.Draw(im)


# ==================================================== 图1  ACL 实验拓扑
im, d = canvas(1500, 880)
title(d, "图1  ACL 实验拓扑（核心三层交换机 + 两台接入交换机）",
      "VLAN2=teacher / VLAN3=stu / VLAN4=server；ACL 挂在核心交换机的 SVI 上")

device(d, (170, 120), "teacher1", "VLAN2", PC_FILL, "pc", w=90, h=48, label_above=True)
device(d, (430, 120), "teacher2", "VLAN2", PC_FILL, "pc", w=90, h=48, label_above=True)
device(d, (600, 120), "teacher3", "VLAN2", PC_FILL, "pc", w=90, h=48, label_above=True)
device(d, (300, 250), "核心交换机", "3560-24PS", SWITCH_FILL, "switch", w=160, h=64,
       label_side="left")
device(d, (310, 430), "student", "2960-24TT", SWITCH_FILL, "switch", w=150, h=60,
       label_side="left")
device(d, (180, 580), "stu1", "VLAN3", PC_FILL, "pc", w=90, h=48)
device(d, (340, 580), "stu2", "VLAN3", PC_FILL, "pc", w=90, h=48)
device(d, (500, 580), "stu3", "VLAN3", PC_FILL, "pc", w=90, h=48)
device(d, (760, 250), "Server", "2960-24TT", SWITCH_FILL, "switch", w=150, h=60,
       label_above=True)
device(d, (620, 430), "Server0", "VLAN4", SRV_FILL, "server", w=110, h=58)
device(d, (790, 430), "Server1", "VLAN4", SRV_FILL, "server", w=110, h=58)
device(d, (960, 430), "Server2", "VLAN4", SRV_FILL, "server", w=110, h=58)
device(d, (1000, 120), "Router0", "1841", ROUTER_FILL, w=115, h=58, label_above=True)
device(d, (1290, 120), "Router1", "1841", ROUTER_FILL, w=115, h=58, label_above=True)

link(d, (215, 168), (340, 250))
link(d, (475, 168), (400, 250))
link(d, (645, 168), (425, 250))
link(d, (380, 314), (385, 430))
link(d, (340, 490), (225, 580))
link(d, (380, 490), (385, 580))
link(d, (420, 490), (545, 580))
link(d, (460, 282), (760, 282))
link(d, (790, 310), (675, 430))
link(d, (835, 310), (845, 430))
link(d, (880, 310), (1015, 430))
link(d, (460, 268), (1000, 160), width=3)
link(d, (1115, 149), (1290, 149), color=SER, width=3)

iface(d, (215, 168), (340, 250), "Fa0/2", frac=0.62, off=-15)
iface(d, (475, 168), (400, 250), "Fa0/3", frac=0.50, off=15)
iface(d, (645, 168), (425, 250), "Fa0/4", frac=0.52, off=-15)
iface(d, (380, 314), (385, 430), "Fa0/5", frac=0.30, off=16)
iface(d, (380, 314), (385, 430), "Fa0/24", frac=0.72, off=16)
iface(d, (340, 490), (225, 580), "Fa0/1", frac=0.60, off=17)
iface(d, (380, 490), (385, 580), "Fa0/2", frac=0.55, off=17)
iface(d, (420, 490), (545, 580), "Fa0/3", frac=0.60, off=17)
iface(d, (460, 282), (760, 282), "Fa0/6", frac=0.10, off=-15)
iface(d, (460, 282), (760, 282), "Fa0/24", frac=0.90, off=-15)
iface(d, (790, 310), (675, 430), "Fa0/1", frac=0.62, off=-17)
iface(d, (835, 310), (845, 430), "Fa0/2", frac=0.40, off=17)
iface(d, (880, 310), (1015, 430), "Fa0/3", frac=0.62, off=17)
iface(d, (460, 268), (1000, 160), "Fa0/1", frac=0.08, off=-15)
iface(d, (460, 268), (1000, 160), "Fa0/0", frac=0.92, off=-15)
iface(d, (1115, 149), (1290, 149), "Se0/0/0", frac=0.22, off=-15)
iface(d, (1115, 149), (1290, 149), "Se0/0/0", frac=0.78, off=-15)

d.text((1202, 112), "Internet", font=font(14, "Internet"), fill=WARN, anchor="mm")
note(d, (1348, 208), ["R1 Loopback0", "200.0.90.100/32"], color=WARN, size=11,
     anchor="ma")

note(d, (30, 330), ["核心交换机 Fa0/1 用 no switchport 变三层口，", "与 Router0 用 /30 互联。"],
     color=OK, size=11)
note(d, (1030, 330), ["ACL 挂载：VLAN2 in / VLAN3 in /", "VLAN4 in + out / R0 外网口 in"],
     color=OK, size=11)

table(d, (30, 670), [
    ["VLAN2 teacher", "192.168.90.0/26", "SVI VLAN2 = .1", "t1 .10 / t2 .11 / t3 .12"],
    ["VLAN3 stu", "192.168.90.64/26", "SVI VLAN3 = .65", "s1 .74 / s2 .75 / s3 .76"],
    ["VLAN4 server", "192.168.90.128/26", "SVI VLAN4 = .129", "S0 .138 / S1 .139 / S2 .140"],
    ["core—R0", "192.168.90.192/30", "core Fa0/1 = .193", "R0 Fa0/0 = .194"],
    ["R0—R1", "200.0.90.0/30", "R0 Se0/0/0 = .1", "R1 Se0/0/0 = .2"],
], widths=[135, 185, 185, 215])
table(d, (770, 670), [
    ["Internet", "200.0.90.0/24", "R1 Lo0 = 200.0.90.100/32", "模拟 Internet 主机"],
    ["R1 静态路由", "—", "ip route 0.0.0.0 0.0.0.0 .1", "回程指向 R0"],
], widths=[135, 185, 205, 195])

im.save(os.path.join(OUT, "fig1_acl.png"))
print("fig1_acl ok")

# ==================================================== 图2  NAT 实验拓扑
im, d = canvas(1700, 900)
title(d, "图2  NAT 实验拓扑（动态 NAT + 静态 PAT）",
      "内网 192.168.90.0/24，公网 200.0.90.0/24；NAT 路由器上区分 inside / outside")

device(d, (160, 120), "teacher1", "VLAN2", PC_FILL, "pc", w=90, h=48, label_above=True)
device(d, (420, 120), "teacher2", "VLAN2", PC_FILL, "pc", w=90, h=48, label_above=True)
device(d, (590, 120), "teacher3", "VLAN2", PC_FILL, "pc", w=90, h=48, label_above=True)
device(d, (290, 250), "核心交换机", "3560-24PS", SWITCH_FILL, "switch", w=160, h=64,
       label_side="left")
device(d, (300, 430), "student", "2960-24TT", SWITCH_FILL, "switch", w=150, h=60,
       label_side="left")
device(d, (170, 580), "stu1", "VLAN3", PC_FILL, "pc", w=90, h=48)
device(d, (330, 580), "stu2", "VLAN3", PC_FILL, "pc", w=90, h=48)
device(d, (490, 580), "stu3", "VLAN3", PC_FILL, "pc", w=90, h=48)
device(d, (880, 430), "Server", "2960-24TT", SWITCH_FILL, "switch", w=150, h=60,
       label_above=True)
device(d, (910, 580), "web服务器", "VLAN4", SRV_FILL, "server", w=130, h=58)
device(d, (700, 250), "NAT路由器", "1841", ROUTER_FILL, w=130, h=64, label_above=True)
device(d, (1000, 250), "Internet路由器", "1841", ROUTER_FILL, w=150, h=64,
       label_above=True)
device(d, (1290, 250), "外网网络", "2960-24TT", SWITCH_FILL, "switch", w=150, h=60,
       label_above=True)
device(d, (1170, 430), "外网用户", "PC-PT", PC_FILL, "pc", w=110, h=52)
device(d, (1400, 430), "外网服务器", "Server-PT", SRV_FILL, "server", w=125, h=58)

link(d, (205, 168), (330, 250))
link(d, (465, 168), (390, 250))
link(d, (635, 168), (415, 250))
link(d, (370, 314), (375, 430))
link(d, (330, 490), (215, 580))
link(d, (370, 490), (375, 580))
link(d, (410, 490), (535, 580))
link(d, (450, 268), (700, 282))
link(d, (450, 305), (900, 455))
link(d, (975, 490), (975, 580))
link(d, (830, 282), (1000, 282), color=SER, width=3)
link(d, (1150, 282), (1290, 282))
link(d, (1320, 310), (1225, 430))
link(d, (1400, 310), (1460, 430))

iface(d, (205, 168), (330, 250), "Fa0/2", frac=0.62, off=-15)
iface(d, (465, 168), (390, 250), "Fa0/3", frac=0.50, off=15)
iface(d, (635, 168), (415, 250), "Fa0/4", frac=0.52, off=-15)
iface(d, (370, 314), (375, 430), "Fa0/5", frac=0.30, off=16)
iface(d, (370, 314), (375, 430), "Fa0/24", frac=0.72, off=16)
iface(d, (330, 490), (215, 580), "Fa0/1", frac=0.60, off=17)
iface(d, (370, 490), (375, 580), "Fa0/2", frac=0.55, off=17)
iface(d, (410, 490), (535, 580), "Fa0/3", frac=0.60, off=17)
iface(d, (450, 268), (700, 282), "Fa0/1", frac=0.07, off=-15)
iface(d, (450, 268), (700, 282), "Fa0/0", frac=0.93, off=-15)
iface(d, (450, 305), (900, 455), "Fa0/6", frac=0.10, off=17)
iface(d, (450, 305), (900, 455), "Fa0/24", frac=0.90, off=17)
iface(d, (975, 490), (975, 580), "Fa0/1", frac=0.50, off=22)
iface(d, (830, 282), (1000, 282), "Se0/0/0", frac=0.22, off=-15)
iface(d, (830, 282), (1000, 282), "Se0/0/0", frac=0.78, off=-15)
iface(d, (1150, 282), (1290, 282), "Fa0/0", frac=0.22, off=-15)
iface(d, (1150, 282), (1290, 282), "Fa0/1", frac=0.78, off=-15)
iface(d, (1320, 310), (1225, 430), "Fa0/2", frac=0.55, off=17)
iface(d, (1400, 310), (1460, 430), "Fa0/3", frac=0.55, off=-17)

d.text((915, 250), "Internet", font=font(14, "Internet"), fill=WARN, anchor="mm")
note(d, (700, 336), ["NAT路由器：Fa0/0 = inside", "Se0/0/0 = outside"],
     color=OK, size=11, anchor="ma")
note(d, (30, 330), ["核心交换机跑内网路由，", "默认路由指向 NAT 路由器 .194。"],
     color=OK, size=11)

table(d, (30, 670), [
    ["VLAN2 teacher", "192.168.90.0/26", "SVI VLAN2 = .1", "t1 .10 / t2 .11 / t3 .12"],
    ["VLAN3 stu", "192.168.90.64/26", "SVI VLAN3 = .65", "s1 .74 / s2 .75 / s3 .76"],
    ["VLAN4 server", "192.168.90.128/26", "SVI VLAN4 = .129", "web服务器 = .138"],
    ["core—NAT", "192.168.90.192/30", "core Fa0/1 = .193", "NAT Fa0/0 = .194"],
    ["NAT 公网池", "200.0.90.16/28", "池 .17 ~ .22（动态 NAT）", "静态 PAT 用 .30"],
], widths=[135, 185, 205, 215])
table(d, (800, 670), [
    ["NAT—Internet", "200.0.90.0/30", "NAT Se0/0/0 = .1", "Internet Se0/0/0 = .2"],
    ["外网 LAN", "200.0.90.8/29", "Internet Fa0/0 = .9", "外网服务器 .10 / 外网用户 .11"],
], widths=[135, 185, 205, 235])

im.save(os.path.join(OUT, "fig2_nat.png"))
print("fig2_nat ok")

# ==================================================== 总览图
a = Image.open(os.path.join(OUT, "fig1_acl.png")).convert("RGB")
b = Image.open(os.path.join(OUT, "fig2_nat.png")).convert("RGB")
W = max(a.width, b.width) + 60
H = a.height + b.height + 80
ov = Image.new("RGB", (W, H), (247, 248, 250))
ov.paste(a, (30, 20))
ov.paste(b, (30, a.height + 60))
dr = ImageDraw.Draw(ov)
dr.rectangle([30, 20, 30 + a.width, 20 + a.height], outline=(170, 175, 185), width=2)
dr.rectangle([30, a.height + 60, 30 + b.width, a.height + 60 + b.height],
             outline=(170, 175, 185), width=2)
ov.save(os.path.join(OUT, "fig_overview2.png"))
print("fig_overview2 ok", ov.size)
