# -*- coding: utf-8 -*-
"""验证实验二两个 pkt：用 PT 打开并重存，再解密比对 RUNNINGCONFIG。

PT 重存时会删掉它不认识/不接受的行，所以"重存后还在"才是真的被接受。
用法：先跑 build_pkts2.py，再跑本脚本（本脚本自己调用 PT）。
"""
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pktlib

PKTS = os.path.join(os.path.dirname(HERE), "03-工程文件")
EXE = r"E:\Cisco Packet Tracer 8.2.2\bin\PacketTracer.exe"

TARGETS = [
    ("90-实验二一-ACL配置.pkt", [
        "ip routing",
        "interface Vlan2",
        " ip address 192.168.90.1 255.255.255.192",
        " ip access-group 120 in",
        " ip access-group 110 out",
        " ip access-group 130 in",
        "access-list 110 deny icmp any 192.168.90.128 0.0.0.63 echo",
        "access-list 110 permit tcp host 192.168.90.10 192.168.90.128 0.0.0.63 eq telnet",
        "access-list 110 deny tcp any 192.168.90.128 0.0.0.63 eq telnet",
        "access-list 120 permit tcp 192.168.90.64 0.0.0.63 host 192.168.90.138 eq www",
        "access-list 120 deny ip 192.168.90.64 0.0.0.63 192.168.90.128 0.0.0.63",
        "access-list 130 deny ip 192.168.90.128 0.0.0.63 200.0.90.0 0.0.0.255",
        " no switchport",
        "ip route 0.0.0.0 0.0.0.0 192.168.90.194",
        "ip route 192.168.90.0 255.255.255.0 192.168.90.193",
        "interface Loopback0",
        " ip address 200.0.90.100 255.255.255.255",
        "hostname Router0",
        "hostname Router1",
    ]),
    ("90-实验二二-NAT配置.pkt", [
        "ip routing",
        "interface Vlan4",
        " ip address 192.168.90.129 255.255.255.192",
        " ip nat inside",
        " ip nat outside",
        "ip nat pool PUB 200.0.90.17 200.0.90.22 netmask 255.255.255.240",
        "ip nat inside source list 1 pool PUB",
        "ip nat inside source static tcp 192.168.90.138 80 200.0.90.30 80",
        "access-list 1 permit 192.168.90.0 0.0.0.255",
        "ip route 200.0.90.16 255.255.255.240 200.0.90.1",
        "ip route 0.0.0.0 0.0.0.0 200.0.90.2",
    ]),
]


def pt_open_save(pkt):
    subprocess.run(["taskkill", "/F", "/IM", "PacketTracer.exe"],
                   capture_output=True)
    time.sleep(1.0)
    subprocess.Popen([EXE, pkt])
    # 等主窗口出现
    hwnd = None
    for _ in range(40):
        time.sleep(1.0)
        ps = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-Process -Name PacketTracer -ErrorAction SilentlyContinue | "
             "Where-Object { $_.MainWindowTitle } | Select-Object -First 1).Id"],
            capture_output=True, text=True)
        if ps.stdout.strip():
            hwnd = ps.stdout.strip()
            break
    if not hwnd:
        return False
    time.sleep(6.0)
    subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "$ws = New-Object -ComObject WScript.Shell; "
         "$ws.AppActivate(%s) | Out-Null; Start-Sleep -Milliseconds 700; "
         "$ws.SendKeys('^s')" % hwnd], capture_output=True)
    time.sleep(5.0)
    return True


def cfg_lines(path):
    """返回 (全部设备配置拼起来的大字符串, 原始 xml)。"""
    x = pktlib.load(path).decode("utf-8", "replace")
    out = []
    for m in re.finditer(r"<DEVICE>(.*?)</DEVICE>", x, re.S):
        blk = m.group(1)
        i = blk.find("<RUNNINGCONFIG>")
        j = blk.find("</RUNNINGCONFIG>")
        out.extend(re.findall(r"<LINE>([^<]*)</LINE>", blk[i:j]))
    return out, x


def main():
    ok_all = True
    for fn, expects in TARGETS:
        path = os.path.join(PKTS, fn)
        before = os.path.getsize(path)
        print("\n==== %s  (%d bytes)" % (fn, before))
        if not pt_open_save(path):
            print("  !! PT 窗口没起来")
            ok_all = False
            continue
        after = os.path.getsize(path)
        print("  重存后 %d bytes %s" % (after, "(已重写)" if after != before else "(未变)"))
        lines, xml = cfg_lines(path)
        print("  VERSION =", re.search(r"<VERSION>([^<]*)</VERSION>", xml).group(1))
        print("  设备 %d 台，链路 %d 条，配置 %d 行"
              % (xml.count("<DEVICE>"), xml.count("<LINK>"), len(lines)))
        joined = "\n".join(lines)
        for e in expects:
            hit = e in joined
            if not hit:
                ok_all = False
            print("   %s  %s" % ("OK " if hit else "MISS", e.strip()))
    print("\n全部通过" if ok_all else "\n有缺失，需检查")


if __name__ == "__main__":
    main()
