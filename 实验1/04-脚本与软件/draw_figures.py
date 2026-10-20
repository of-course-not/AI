# -*- coding: utf-8 -*-
"""Draw lab topology figures for the report.

Layout rule: devices + interface names only; every subnet goes into a compact
address table at the bottom, so nothing overlaps and the figure stays readable.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))   # ...\实验1\04-脚本与软件
OUT = os.path.join(os.path.dirname(HERE), "06-图表与截图")
os.makedirs(OUT, exist_ok=True)

CJK_PATH = r"C:\Windows\Fonts\simhei.ttf"
MONO_PATH = r"C:\Windows\Fonts\consola.ttf"

BG = (255, 255, 255)
LINE = (45, 45, 45)
SER = (192, 45, 45)
ROUTER_FILL = (220, 234, 248)
SWITCH_FILL = (226, 240, 217)
PC_FILL = (252, 238, 218)
NET = (22, 62, 140)
WARN = (150, 32, 32)
OK = (20, 96, 45)
GREY = (95, 95, 95)
GRID = (205, 210, 220)
HEAD_FILL = (233, 238, 246)


def _has_cjk(text):
    """Any non-ASCII character -> use the CJK font (Consolas lacks CJK punctuation)."""
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
            d.text((cx, y - 45), sub, font=font(12, sub), fill=GREY, anchor="ma")
    else:
        d.text((cx, y + h + 6), label, font=font(15, label), fill=(12, 12, 12), anchor="ma")
        if sub:
            d.text((cx, y + h + 26), sub, font=font(12, sub), fill=GREY, anchor="ma")
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


# ======================================= 图0  实验一：基本配置 + 单臂路由
im, d = canvas(1180, 780)
title(d, "图0  实验一（路由器基本配置与单臂路由）拓扑",
      "自设计拓扑：R1 用 Fa0/0 的两个子接口实现 VLAN 间路由，R1-R2 为串行链路，R1 另配 Loopback0")

device(d, (170, 250), "SW1", "2960-24TT", SWITCH_FILL, "switch")
device(d, (450, 250), "R1", "1841", ROUTER_FILL)
device(d, (790, 250), "R2", "1841", ROUTER_FILL)
device(d, (120, 450), "PC-A", "VLAN10", PC_FILL, "pc", w=84, h=50)
device(d, (300, 450), "PC-B", "VLAN20", PC_FILL, "pc", w=84, h=50)
device(d, (860, 450), "PC-C", "R2 直连", PC_FILL, "pc", w=84, h=50)

link(d, (274, 278), (450, 278), width=3)
link(d, (554, 278), (790, 278), color=SER, width=3)
link(d, (162, 450), (192, 306))
link(d, (342, 450), (252, 306))
link(d, (902, 450), (902, 306), dashed=True)

iface(d, (274, 278), (450, 278), "Fa0/24", frac=0.07, off=-14)
iface(d, (274, 278), (450, 278), "Fa0/0", frac=0.90, off=-14)
iface(d, (554, 278), (790, 278), "Se0/0/0", frac=0.22, off=-14)
iface(d, (554, 278), (790, 278), "Se0/0/0", frac=0.80, off=-14)
iface(d, (162, 450), (192, 306), "Fa0/1", frac=0.60, off=16)
iface(d, (342, 450), (252, 306), "Fa0/2", frac=0.60, off=16)
iface(d, (902, 450), (902, 306), "Fa0/0", frac=0.42, off=24)

# Trunk 说明（开关上方空白处）
note(d, (30, 178), ["SW1 Fa0/24 为 Trunk 口（dot1Q 封装）"], color=OK, size=12)
link(d, (200, 196), (208, 246), color=OK, width=1, dashed=True)
# 子接口说明
note(d, (576, 340), ["R1 单臂路由子接口：", "Fa0/0.10 = 192.168.90.1",
                     "Fa0/0.20 = 192.168.90.65"], color=WARN, size=12)
link(d, (572, 352), (536, 306), color=WARN, width=1, dashed=True)

# Loopback0
link(d, (502, 250), (502, 206), color=OK, width=2, dashed=True)
d.ellipse([498, 200, 506, 208], fill=OK)
note(d, (516, 194), ["Loopback0  192.168.90.200/32"], color=OK, size=12)

table(d, (30, 580), [
    ["VLAN10", "192.168.90.0/26", "R1 Fa0/0.10 = .1", "PC-A = .10"],
    ["VLAN20", "192.168.90.64/26", "R1 Fa0/0.20 = .65", "PC-B = .74"],
    ["R1—R2", "192.168.90.128/30", "R1 Se0/0/0 = .129", "R2 Se0/0/0 = .130"],
    ["PC-C 段", "192.168.90.132/30", "R2 Fa0/0 = .133", "PC-C = .134"],
    ["Loopback0", "192.168.90.200/32", "R1 Lo0", "—"],
], widths=[110, 190, 215, 195])

im.save(os.path.join(OUT, "fig0_basic.png"))
print("fig0 ok")

# ======================================= 图1  实验二：静态路由 + 三层交换机
im, d = canvas(1370, 800)
title(d, "图1  静态路由与三层交换机实验拓扑",
      "全部地址位于 192.168.90.0/24：两个 VLAN 用 /26，路由器之间与 PC 直连段用 /30")

sw0 = device(d, (190, 300), "Switch0", "3560-24PS 三层", SWITCH_FILL, "switch", label_above=True)
r0 = device(d, (470, 300), "Router0", "1841", ROUTER_FILL)
r1 = device(d, (750, 300), "Router1", "1841", ROUTER_FILL)
r2 = device(d, (1048, 300), "Router2", "1841", ROUTER_FILL, label_above=True)
device(d, (300, 150), "PC4", "R0 直连", PC_FILL, "pc", w=84, h=50, label_above=True)
device(d, (768, 118), "PC2", "R1 直连", PC_FILL, "pc", w=84, h=50, label_above=True)
device(d, (110, 470), "PC0", "VLAN2", PC_FILL, "pc", w=84, h=50)
device(d, (300, 470), "PC1", "VLAN3", PC_FILL, "pc", w=84, h=50)
device(d, (1058, 470), "PC3", "R2 直连", PC_FILL, "pc", w=84, h=50)

link(d, (294, 328), (470, 328), width=3)
link(d, (574, 328), (750, 328), color=SER, width=3)
link(d, (854, 328), (1048, 328), color=SER, width=3)
link(d, (152, 470), (232, 356))
link(d, (342, 470), (262, 356))
link(d, (342, 200), (476, 300), dashed=True)
link(d, (810, 168), (810, 300), dashed=True)
link(d, (1132, 470), (1132, 356), dashed=True)

iface(d, (294, 328), (470, 328), "Fa0/1", frac=0.12, off=-14)
iface(d, (294, 328), (470, 328), "Fa0/0", frac=0.88, off=-14)
iface(d, (574, 328), (750, 328), "Se0/0/0", frac=0.22, off=-14)
iface(d, (574, 328), (750, 328), "Se0/0/0", frac=0.80, off=-14)
iface(d, (854, 328), (1048, 328), "Se0/0/1", frac=0.20, off=-14)
iface(d, (854, 328), (1048, 328), "Se0/0/0", frac=0.80, off=-14)
iface(d, (152, 470), (232, 356), "Fa0/2", frac=0.62, off=16)
iface(d, (342, 470), (262, 356), "Fa0/3", frac=0.62, off=16)
iface(d, (342, 200), (476, 300), "Fa0/1", frac=0.62, off=16)
iface(d, (810, 168), (810, 300), "Fa0/0", frac=0.55, off=24)
iface(d, (1132, 470), (1132, 356), "Fa0/0", frac=0.45, off=24)

note(d, (392, 442), ["Switch0 为 3560-24PS 三层交换机",
                     "已启用 ip routing",
                     "SVI：VLAN2 = .1    VLAN3 = .65",
                     "Fa0/1 用 no switchport 变三层口 = .129/30"], color=WARN, size=12)

table(d, (30, 640), [
    ["VLAN2", "192.168.90.0/26", "SW0 SVI VLAN2 = .1", "PC0 = .10"],
    ["VLAN3", "192.168.90.64/26", "SW0 SVI VLAN3 = .65", "PC1 = .74"],
    ["SW0—R0", "192.168.90.128/30", "SW0 Fa0/1 = .129", "R0 Fa0/0 = .130"],
    ["R0—PC4", "192.168.90.132/30", "R0 Fa0/1 = .133", "PC4 = .134"],
], widths=[100, 185, 205, 165])
table(d, (700, 640), [
    ["R0—R1", "192.168.90.136/30", "R0 Se0/0/0 = .137", "R1 Se0/0/0 = .138"],
    ["R1—PC2", "192.168.90.140/30", "R1 Fa0/0 = .141", "PC2 = .142"],
    ["R1—R2", "192.168.90.144/30", "R1 Se0/0/1 = .145", "R2 Se0/0/0 = .146"],
    ["R2—PC3", "192.168.90.148/30", "R2 Fa0/0 = .149", "PC3 = .150"],
], widths=[100, 185, 205, 165])

im.save(os.path.join(OUT, "fig1_static.png"))
print("fig1 ok")

# ======================================= 图2  实验三：RIP
im, d = canvas(1200, 700)
title(d, "图2  RIP 实验拓扑（2621XM + WIC-2T 替代原 2501）",
      "5 个网段统一使用 /27：RIPv1 通告不携带掩码，同主网内掩码不一致会学错路由；"
      "接口名：原 E0→Fa0/0，原 S0→Se0/0，原 S1→Se0/1")

device(d, (70, 240), "2621A", "2621XM", ROUTER_FILL)
device(d, (320, 240), "2501A", "2621XM", ROUTER_FILL)
device(d, (590, 240), "2501B", "2621XM", ROUTER_FILL, label_above=True)
device(d, (860, 240), "2501C", "2621XM", ROUTER_FILL, label_above=True)
device(d, (598, 430), "PC2", "网段④", PC_FILL, "pc", w=84, h=50)
device(d, (868, 430), "PC1", "网段⑤", PC_FILL, "pc", w=84, h=50)

link(d, (174, 268), (320, 268), width=3)
link(d, (424, 268), (590, 268), color=SER, width=3)
link(d, (694, 268), (860, 268), color=SER, width=3)
link(d, (640, 430), (640, 296))
link(d, (910, 430), (910, 296))

iface(d, (174, 268), (320, 268), "F0/0", frac=0.20, off=-14)
iface(d, (174, 268), (320, 268), "F0/0", frac=0.80, off=-14)
iface(d, (424, 268), (590, 268), "S0/0", frac=0.20, off=-14)
iface(d, (424, 268), (590, 268), "S0/0", frac=0.80, off=-14)
iface(d, (694, 268), (860, 268), "S0/1", frac=0.20, off=-14)
iface(d, (694, 268), (860, 268), "S0/0", frac=0.80, off=-14)
iface(d, (640, 430), (640, 296), "F0/0", frac=0.50, off=22)
iface(d, (910, 430), (910, 296), "F0/0", frac=0.50, off=22)

table(d, (30, 520), [
    ["①", "192.168.90.0/27", "2621A F0/0 = .1", "2501A F0/0 = .2"],
    ["②", "192.168.90.32/27", "2501A S0/0 = .33", "2501B S0/0 = .34"],
    ["③", "192.168.90.64/27", "2501B S0/1 = .65", "2501C S0/0 = .66"],
    ["④", "192.168.90.96/27", "2501B F0/0 = .97", "PC2 = .98"],
    ["⑤", "192.168.90.128/27", "2501C F0/0 = .129", "PC1 = .130"],
], widths=[50, 195, 210, 185])

note(d, (700, 540), ["RIPv1 使用有类路由，", "network 语句只需写主网 192.168.90.0，",
                     "路由器按接口实际掩码（/27）通告。",
                     "PT 8.2.2 无 2501 型号，设备名沿用原图，", "实际机型为 2621XM。"],
     color=GREY, size=11)
im.save(os.path.join(OUT, "fig2_rip.png"))
print("fig2 ok")




# ======================================= 图3  实验四：OSPF 多区域
im, d = canvas(1360, 960)
title(d, "图3  OSPF 多区域实验拓扑（Area 0 / Area 1 / Area 2）",
      "Router1、Router3 为 ABR（同时属于 Area 0 与另一个区域）；PC 按任务要求补接，原图未画出 PC")

# ---------- Area 0
device(d, (200, 470), "Router0", "1841", ROUTER_FILL, label_above=True)
device(d, (120, 700), "Switch0", "2950-24", SWITCH_FILL, "switch", w=96, h=50)
device(d, (270, 700), "PC0", "Area0", PC_FILL, "pc", w=80, h=50)

# ---------- Area 1
device(d, (860, 470), "Router1", "1841  ABR", ROUTER_FILL, label_above=True)
device(d, (880, 700), "Switch1", "2950-24", SWITCH_FILL, "switch", w=96, h=50)
device(d, (1030, 700), "Router2", "1841", ROUTER_FILL)
device(d, (1180, 700), "PC1", "Area1", PC_FILL, "pc", w=80, h=50)

# ---------- Area 2
device(d, (560, 340), "Router3", "1841  ABR", ROUTER_FILL)
device(d, (640, 160), "Switch2", "2960-24TT", SWITCH_FILL, "switch", w=96, h=50,
       label_above=True)
device(d, (420, 150), "Router5", "1841", ROUTER_FILL)
device(d, (800, 150), "Router4", "1841", ROUTER_FILL)
device(d, (690, 270), "PC2", "Area2", PC_FILL, "pc", w=80, h=46)

# ---------- 链路
link(d, (222, 526), (168, 700))                        # R0 - Switch0
link(d, (216, 725), (270, 725))                        # Switch0 - PC0
link(d, (304, 498), (860, 498), color=SER, width=3)    # R0 - R1
link(d, (296, 472), (566, 394), color=SER, width=3)    # R0 - R3
link(d, (664, 394), (866, 472), color=SER, width=3)    # R3 - R1
link(d, (890, 526), (910, 700))                        # R1 - Switch1
link(d, (976, 725), (1030, 725))                       # Switch1 - R2
link(d, (1134, 725), (1180, 725))                      # R2 - PC1
link(d, (660, 210), (612, 340))                        # Switch2 - R3
link(d, (524, 188), (640, 188))                        # R5 - Switch2
link(d, (736, 188), (800, 188))                        # Switch2 - R4
link(d, (688, 210), (730, 270))                        # Switch2 - PC2

# ---------- 接口名
iface(d, (222, 526), (168, 700), "Fa0/0", frac=0.22, off=-16)
iface(d, (222, 526), (168, 700), "Fa0/1", frac=0.74, off=22)
iface(d, (216, 725), (270, 725), "Fa0/2", frac=0.18, off=-16)
iface(d, (304, 498), (860, 498), "Se0/0/0", frac=0.14, off=-14)
iface(d, (304, 498), (860, 498), "Se0/0/0", frac=0.86, off=-14)
iface(d, (296, 472), (566, 394), "Se0/0/1", frac=0.22, off=-16)
iface(d, (296, 472), (566, 394), "Se0/0/0", frac=0.74, off=16)
iface(d, (664, 394), (866, 472), "Se0/0/1", frac=0.26, off=16)
iface(d, (664, 394), (866, 472), "Se0/0/1", frac=0.78, off=-16)
iface(d, (890, 526), (910, 700), "Fa0/0", frac=0.26, off=22)
iface(d, (890, 526), (910, 700), "Fa0/1", frac=0.74, off=-16)
iface(d, (976, 725), (1030, 725), "Fa0/2", frac=0.18, off=-16)
iface(d, (1134, 725), (1180, 725), "Fa0/0", frac=0.15, off=-16)
iface(d, (660, 210), (612, 340), "Fa0/3", frac=0.62, off=-14)
iface(d, (524, 188), (640, 188), "Fa0/1", frac=0.82, off=-16)
iface(d, (736, 188), (800, 188), "Fa0/2", frac=0.18, off=-16)
iface(d, (688, 210), (730, 270), "Fa0/4", frac=0.42, off=-14)

# ---------- 区域标注
d.text((330, 560), "Area 0", font=font(24, "Area 0"), fill=(30, 30, 30))
d.text((1000, 560), "Area 1", font=font(22, "Area 1"), fill=(30, 30, 30))
d.text((900, 300), "Area 2", font=font(22, "Area 2"), fill=(30, 30, 30))

# ---------- 地址表
table(d, (30, 830), [
    ["Area0 LAN", "192.168.90.0/26", "R0 Fa0/0 = .1", "PC0 = .10"],
    ["Area1 LAN", "192.168.90.64/26", "R1 .65    R2 .66", "PC1 = .74"],
    ["Area2 LAN", "192.168.90.128/26", "R3 .129  R4 .130  R5 .131", "PC2 = .138"],
], widths=[110, 180, 250, 130])
table(d, (740, 830), [
    ["R0-R3", "192.168.90.192/30", "R0 = .193", "R3 = .194"],
    ["R0-R1", "192.168.90.196/30", "R0 = .197", "R1 = .198"],
    ["R3-R1", "192.168.90.200/30", "R3 = .201", "R1 = .202"],
], widths=[90, 180, 120, 110])

im.save(os.path.join(OUT, "fig3_ospf.png"))
print("fig3 ok")





