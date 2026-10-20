# -*- coding: utf-8 -*-
"""Compose the four topology figures into one overview figure for page 1."""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "06-图表与截图")
CJK = r"C:\Windows\Fonts\simhei.ttf"

names = ["fig0_basic.png", "fig1_static.png", "fig2_rip.png", "fig3_ospf.png"]
tags = ["(a) 实验一  路由器基本配置与单臂路由",
        "(b) 实验二  静态路由与三层交换机",
        "(c) 实验三  RIP 路由协议",
        "(d) 实验四  OSPF 多区域"]

PANEL_W, PANEL_H = 900, 620
PAD = 18
TAG_H = 34

W = PANEL_W * 2 + PAD * 3
H = (PANEL_H + TAG_H) * 2 + PAD * 3
canvas = Image.new("RGB", (W, H), (255, 255, 255))
draw = ImageDraw.Draw(canvas)
f = ImageFont.truetype(CJK, 20)

for idx, (name, tag) in enumerate(zip(names, tags)):
    im = Image.open(os.path.join(HERE, name)).convert("RGB")
    scale = min(PANEL_W / im.width, PANEL_H / im.height)
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    col, row = idx % 2, idx // 2
    px = PAD + col * (PANEL_W + PAD)
    py = PAD + row * (PANEL_H + TAG_H + PAD)
    canvas.paste(im, (px + (PANEL_W - im.width) // 2, py + TAG_H + (PANEL_H - im.height) // 2))
    draw.text((px + 4, py + 6), tag, font=f, fill=(20, 20, 20))
    draw.rectangle([px, py, px + PANEL_W, py + TAG_H + PANEL_H], outline=(190, 195, 205))

canvas.save(os.path.join(HERE, "fig_overview.png"))
print("overview ok", canvas.size)
