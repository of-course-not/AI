# -*- coding: utf-8 -*-
"""判定 PT 是否真的加载了某个 pkt。

判据：加载成功时窗口标题是 "Cisco Packet Tracer - <完整路径>"，
加载失败时只有 "Cisco Packet Tracer"。
用法：python pt_probe.py <pkt> [更多 pkt...]
"""
import os
import subprocess
import sys
import time

EXE = r"E:\Cisco Packet Tracer 8.2.2\bin\PacketTracer.exe"


def probe(pkt):
    pkt = os.path.abspath(pkt)
    subprocess.run(["taskkill", "/F", "/IM", "PacketTracer.exe"], capture_output=True)
    time.sleep(1.2)
    subprocess.Popen([EXE, pkt])
    title = ""
    ok = False
    saw_loading = False
    t0 = time.time()
    for _ in range(70):
        time.sleep(1.0)
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-Process -Name PacketTracer -ErrorAction SilentlyContinue | "
             "Where-Object { $_.MainWindowTitle } | Select-Object -First 1).MainWindowTitle"],
            capture_output=True, text=True)
        t = r.stdout.strip()
        if t:
            title = t
        if "Please wait" in title:
            saw_loading = True
            continue
        # 判据：标题里带 ".pkt" 就算加载成功。不要比对文件名——PowerShell 回传
        # 中文路径会被当成 GBK 解码成乱码，中文文件名永远比不上。
        if title.lower().endswith(".pkt"):
            ok = True
            break
        if saw_loading and title == "Cisco Packet Tracer" and time.time() - t0 > 8:
            break
        if title == "Cisco Packet Tracer" and time.time() - t0 > 45:
            break
    subprocess.run(["taskkill", "/F", "/IM", "PacketTracer.exe"], capture_output=True)
    return ok, title


def main():
    for p in sys.argv[1:]:
        ok, title = probe(p)
        print("%s  %s" % ("LOAD-OK " if ok else "LOAD-FAIL", os.path.basename(p)))
        print("    title=%r" % title)


if __name__ == "__main__":
    main()
