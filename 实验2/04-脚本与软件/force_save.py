# -*- coding: utf-8 -*-
"""用 PT 打开指定 pkt 并强制重存，用于验证命令是否被 PT 接受。

PT 重存时会删掉它不认识的命令行，所以"重存后还在"才是真的被接受。
用法：python force_save.py <pkt路径> [等待秒数]
"""
import os
import subprocess
import sys
import time

EXE = r"E:\Cisco Packet Tracer 8.2.2\bin\PacketTracer.exe"


def main():
    pkt = os.path.abspath(sys.argv[1])
    wait = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    before = os.path.getsize(pkt)

    subprocess.run(["taskkill", "/F", "/IM", "PacketTracer.exe"], capture_output=True)
    time.sleep(1.2)
    subprocess.Popen([EXE, pkt])

    pid = None
    for _ in range(60):
        time.sleep(1.0)
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-Process -Name PacketTracer -ErrorAction SilentlyContinue | "
             "Where-Object { $_.MainWindowTitle } | Select-Object -First 1).Id"],
            capture_output=True, text=True)
        if r.stdout.strip():
            pid = r.stdout.strip()
            break
    if not pid:
        print("FAIL: PT 窗口没起来")
        return 1

    print("PT pid =", pid, "等待加载 %ds" % wait)
    time.sleep(wait)

    # 连发三次 Ctrl+S，每次之后看文件大小
    for attempt in range(3):
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "$ws = New-Object -ComObject WScript.Shell; "
             "$ws.AppActivate(%s) | Out-Null; Start-Sleep -Milliseconds 900; "
             "$ws.SendKeys('^s')" % pid], capture_output=True)
        time.sleep(6.0)
        now = os.path.getsize(pkt)
        print("  第 %d 次 Ctrl+S 后 %d bytes%s"
              % (attempt + 1, now, "" if now == before else "  <- 已重写"))
        if now != before:
            break

    now = os.path.getsize(pkt)
    if now == before:
        print("WARN: 文件大小没变，PT 可能没真正重写")
        return 2
    print("OK: %d -> %d bytes" % (before, now))
    subprocess.run(["taskkill", "/F", "/IM", "PacketTracer.exe"], capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
