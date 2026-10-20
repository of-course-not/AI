# -*- coding: utf-8 -*-
"""把实验二报告导出为 PDF 并逐页渲染成 PNG，用于目视复核版式。"""
import os
import shutil
import sys

import fitz
import win32com.client

HERE = os.path.dirname(os.path.abspath(__file__))
EXP2 = os.path.dirname(HERE)
DOCX = os.path.join(EXP2, "01-实验报告", "90-实验二-ACL与NAT配置-实验报告.docx")
OUT = os.path.join(EXP2, "06-图表与截图", "_pdf")
PDF = os.path.join(OUT, "report.pdf")

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)

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
for i, page in enumerate(d):
    pix = page.get_pixmap(dpi=110)
    p = os.path.join(OUT, "page%02d.png" % (i + 1))
    pix.save(p)
    print(p, pix.width, pix.height)
