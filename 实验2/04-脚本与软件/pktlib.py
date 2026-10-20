# -*- coding: utf-8 -*-
"""Cisco Packet Tracer .pkt/.pka 编解码（纯 Python）。

算法来源：mircodz/pka2xml (BSD-2) 与 strykey/pka-decipher 的纯 Python Twofish。
流程（解密）：反混淆1 -> Twofish-EAX 解密 -> 反混淆2 -> zlib 解压（前 4 字节为大端原长）。
加密为完全逆过程。
"""
import os
import struct
import sys
import zlib

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "_pkt"))

from twofish import Twofish  # noqa: E402  纯 Python 实现，导入时自带自检

BLOCK = 16
KEY = bytes([137]) * 16
IV = bytes([16]) * 16


def _xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def _shl1(bs):
    out = bytearray(len(bs))
    carry = 0
    for i in reversed(range(len(bs))):
        out[i] = ((bs[i] << 1) & 0xFF) | carry
        carry = (bs[i] & 0x80) >> 7
    return bytes(out)


class _CMAC(object):
    def __init__(self, enc):
        self.enc = enc
        L = enc(bytes(BLOCK))
        k1 = _shl1(L)
        if L[0] & 0x80:
            k1 = _xor(k1, b"\x00" * 15 + b"\x87")
        k2 = _shl1(k1)
        if k1[0] & 0x80:
            k2 = _xor(k2, b"\x00" * 15 + b"\x87")
        self.k1, self.k2 = k1, k2

    def digest(self, data):
        if len(data) == 0:
            last = _xor(b"\x80" + b"\x00" * 15, self.k2)
            blocks = []
        else:
            blocks = [data[i:i + BLOCK] for i in range(0, len(data), BLOCK)]
            if len(blocks[-1]) == BLOCK:
                last = _xor(blocks[-1], self.k1)
            else:
                pad = blocks[-1] + b"\x80"
                pad += b"\x00" * (BLOCK - len(pad))
                last = _xor(pad, self.k2)
            blocks = blocks[:-1]
        x = bytes(BLOCK)
        for b in blocks:
            x = self.enc(_xor(x, b))
        return self.enc(_xor(x, last))


def _ctr(enc, nonce_block, data):
    out = bytearray()
    base = int.from_bytes(nonce_block, "big")
    for i in range(0, len(data), BLOCK):
        ks = enc(((base + i // BLOCK) & ((1 << 128) - 1)).to_bytes(BLOCK, "big"))
        chunk = data[i:i + BLOCK]
        out += _xor(ks, chunk)
    return bytes(out)


def _omac(cmac, prefix, data):
    return cmac.digest(b"\x00" * (BLOCK - 1) + bytes([prefix]) + data)


def _eax_decrypt(enc, cmac, nonce, blob):
    tag, ct = blob[-BLOCK:], blob[:-BLOCK]
    n = _omac(cmac, 0, nonce)
    h = _omac(cmac, 1, b"")
    c = _omac(cmac, 2, ct)
    if _xor(_xor(n, h), c) != tag:
        raise ValueError("EAX tag mismatch: 文件损坏或密钥不对")
    return _ctr(enc, n, ct)


def _eax_encrypt(enc, cmac, nonce, pt):
    n = _omac(cmac, 0, nonce)
    h = _omac(cmac, 1, b"")
    ct = _ctr(enc, n, pt)
    c = _omac(cmac, 2, ct)
    return ct + _xor(_xor(n, h), c)


def is_old(blob):
    """PT5 之前的老格式：仅 xor + zlib，无 Twofish。"""
    n = len(blob)
    if n < 6:
        return False
    return ((blob[4] ^ ((n - 4) & 0xFF)) == 0x78
            and (blob[5] ^ ((n - 5) & 0xFF)) == 0x9C)


def decrypt_old(blob):
    n = len(blob)
    plain = bytes((b ^ ((n - i) & 0xFF)) & 0xFF for i, b in enumerate(blob))
    size = struct.unpack(">I", plain[:4])[0]
    out = zlib.decompress(plain[4:])
    if len(out) != size:
        sys.stderr.write("warning: 声明长度 %d != 实际 %d\n" % (size, len(out)))
    return out


def decrypt(blob):
    """.pkt 字节 -> XML 文本（自动识别老格式 / 新格式）。"""
    if is_old(blob):
        return decrypt_old(blob)
    n = len(blob)
    stage1 = bytes((blob[n + ~i] ^ ((n - i * n) & 0xFF)) & 0xFF for i in range(n))
    tf = Twofish(KEY)
    stage2 = _eax_decrypt(tf.encrypt, _CMAC(tf.encrypt), IV, stage1)
    m = len(stage2)
    stage3 = bytes(stage2[i] ^ ((m - i) & 0xFF) for i in range(m))
    size = struct.unpack(">I", stage3[:4])[0]
    plain = zlib.decompress(stage3[4:])
    if len(plain) != size:
        sys.stderr.write("warning: 声明长度 %d != 实际 %d\n" % (size, len(plain)))
    return plain


def encrypt(xml):
    """XML 文本（str 或 bytes）-> .pkt 字节。"""
    if isinstance(xml, str):
        xml = xml.encode("utf-8")
    comp = zlib.compress(xml, 9)
    stage3 = len(xml).to_bytes(4, "big") + comp
    m = len(stage3)
    stage2 = bytes(stage3[i] ^ ((m - i) & 0xFF) for i in range(m))
    tf = Twofish(KEY)
    stage1 = _eax_encrypt(tf.encrypt, _CMAC(tf.encrypt), IV, stage2)
    n = len(stage1)
    out = bytearray(n)
    for i in range(n):
        out[n + ~i] = stage1[i] ^ ((n - i * n) & 0xFF)
    return bytes(out)


def load(path):
    with open(path, "rb") as f:
        return decrypt(f.read())


def save(path, xml):
    with open(path, "wb") as f:
        f.write(encrypt(xml))


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    data = load(src)
    with open(dst, "wb") as f:
        f.write(data)
    print("decrypted %d bytes -> %s" % (len(data), dst))
