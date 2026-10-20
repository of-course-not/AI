# -*- coding: utf-8 -*-
"""Export the report to PDF with Word COM and render pages to PNG."""
import os
import sys

import fitz
import win32com.client

HERE = os.path.dirname(os.path.abspath(__file__))   # ...\实验1\04-脚本与软件
EXP1 = os.path.dirname(HERE)
DOCX = os.path.join(EXP1, "01-实验报告",
                    "90-实验一-路由器配置与路由协议-实验报告.docx")
PDF = os.path.join(EXP1, "06-图表与截图", "_pdf", "report.pdf")
os.makedirs(os.path.dirname(PDF), exist_ok=True)

word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(DOCX, ReadOnly=False)
    doc.SaveAs2(PDF, FileFormat=17)  # wdFormatPDF
    doc.Close(False)
finally:
    word.Quit()

d = fitz.open(PDF)
print("pages:", d.page_count)
out = os.path.join(HERE, "_check")
for i, page in enumerate(d):
    pix = page.get_pixmap(dpi=110)
    p = os.path.join(out, f"page{i + 1:02d}.png")
    pix.save(p)
    print(p, pix.width, pix.height)
