# -*- coding: utf-8 -*-
"""检查生成的 .pkt：设备/端口/IP/时钟/RUNNINGCONFIG 尾部/LINK 引用。"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pktlib

OUT = os.path.join(os.path.dirname(HERE), "03-工程文件")
FILES = [f for f in os.listdir(OUT) if f.endswith(".pkt") and not f.startswith("_")]


def ports_of(dev):
    out = []
    for m in re.finditer(r"<PORT>(.*?)</PORT>", dev, re.S):
        p = m.group(1)

        def g(tag):
            mm = re.search(r"<%s>(.*?)</%s>" % (tag, tag), p, re.S)
            return mm.group(1) if mm else ""

        out.append(dict(type=g("TYPE"), power=g("POWER"), ip=g("IP"),
                        mask=g("SUBNET"), gw=g("PORT_GATEWAY"),
                        cr=g("CLOCKRATE"), cf=g("CLOCKRATEFLAG"),
                        mac=g("MACADDRESS")))
    return out


for fn in sorted(FILES):
    path = os.path.join(OUT, fn)
    xml = pktlib.load(path)
    if isinstance(xml, bytes):
        xml = xml.decode("utf-8", "replace")
    print("=" * 78)
    print(fn, os.path.getsize(path), "bytes")
    ver = re.search(r"<VERSION>([^<]*)</VERSION>", xml)
    print("  VERSION:", ver.group(1) if ver else "?")
    devs = re.findall(r"<DEVICE>.*?</DEVICE>", xml, re.S)
    print("  devices:", len(devs))
    for d in devs:
        name = re.search(r"<NAME[^>]*>([^<]*)</NAME>", d).group(1)
        model = re.search(r'<TYPE[^>]*model="([^"]*)"', d)
        rc = re.search(r"<RUNNINGCONFIG>(.*?)</RUNNINGCONFIG>", d, re.S)
        rc = rc.group(1) if rc else ""
        lines = [l.strip() for l in rc.split("\n") if l.strip()]
        print("  -- %-10s model=%-10s ports=%d  rc_lines=%d  last=%r"
              % (name, model.group(1) if model else "?", len(ports_of(d)),
                 len(lines), lines[-1] if lines else ""))
        for i, p in enumerate(ports_of(d)):
            if p["ip"] or p["power"] == "true" or p["cr"] not in ("", "0"):
                print("       [%d] %-22s power=%-5s ip=%-16s mask=%-16s "
                      "cr=%-7s cf=%s" % (i, p["type"], p["power"], p["ip"],
                                         p["mask"], p["cr"], p["cf"]))
    links = re.findall(r"<LINK>(.*?)</LINK>", xml, re.S)
    print("  links:", len(links))
    refs = set(re.findall(r"save-ref-id:(\d+)", xml))
    for l in links:
        t = re.search(r"<TYPE>([^<]*)</TYPE>", l)
        fr = re.search(r"<FROM>([^<]*)</FROM>", l)
        to = re.search(r"<TO>([^<]*)</TO>", l)
        ports = re.findall(r"<PORT>([^<]*)</PORT>", l)
        dce = re.search(r"<DCEDEV>([^<]*)</DCEDEV>", l)
        print("    %-12s %s:%s <-> %s:%s %s" % (
            t.group(1) if t else "?",
            (fr.group(1) if fr else "")[-8:], ports[0] if ports else "",
            (to.group(1) if to else "")[-8:], ports[1] if len(ports) > 1 else "",
            ("DCE=" + dce.group(1)[-8:]) if dce else ""))
