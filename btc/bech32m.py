# Copyright (c) 2017, 2020 Pieter Wuille
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# BIP-0173 https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki
# BIP-0350 https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki
# Derived from https://raw.githubusercontent.com/sipa/bech32/master/ref/python/segwit_addr.py
#
# Reference implementation for Bech32/Bech32m and segwit addresses.

import typing

CHARSET = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l'
CONST = 0x2bc830a3


def bech32m_polymod(data: bytearray) -> int:
    # Internal function that computes the Bech32 checksum.
    assert isinstance(data, bytearray)
    gen = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for val in data:
        top = chk >> 25
        chk = chk & 0x1ffffff
        chk = chk << 5 ^ val
        for i in range(5):
            chk ^= gen[i] if ((top >> i) & 1) else 0
    return chk


def bech32m_hrp_expand(hrp: str) -> bytearray:
    # Expand the HRP into values for checksum computation.
    r = bytearray()
    r.extend([ord(x) >> 5 for x in hrp])
    r.append(0)
    r.extend([ord(x) & 31 for x in hrp])
    return r


def bech32m_verify_checksum(hrp: str, data: bytearray) -> bool:
    # Verify a checksum given HRP and converted data characters.
    assert isinstance(data, bytearray)
    return bech32m_polymod(bech32m_hrp_expand(hrp) + bytearray(data)) == CONST


def bech32m_create_checksum(hrp: str, data: bytearray) -> bytearray:
    # Compute the checksum values given HRP and data.
    assert isinstance(data, bytearray)
    data = bech32m_hrp_expand(hrp) + data
    pmod = bech32m_polymod(data + bytearray(6)) ^ CONST
    return bytearray([(pmod >> 5 * (5 - i)) & 31 for i in range(6)])


def bech32m_encode(hrp: str, data: bytearray) -> str:
    # Compute a Bech32 string given HRP and data values.
    assert isinstance(data, bytearray)
    data = data + bech32m_create_checksum(hrp, data)
    return hrp + '1' + ''.join([CHARSET[d] for d in data])


def bech32m_decode(bech: str) -> typing.Tuple[str, bytearray]:
    # Validate a string, and determine HRP and data.
    assert len(bech) <= 90
    for c in bech:
        assert ord(c) >= ord('!')
        assert ord(c) <= ord('~')
    bech = bech.lower()
    pos = bech.rfind('1')
    assert pos > 0
    assert pos + 6 < len(bech)
    for c in bech[pos+1:]:
        assert c in CHARSET
    hrp = bech[:pos]
    data = bytearray([CHARSET.find(x) for x in bech[pos+1:]])
    assert bech32m_verify_checksum(hrp, data)
    return hrp, data[:-6]


def bech32m_re_arrange_5(data: bytearray) -> bytearray:
    # Re-arrange those bits into groups of 5, and pad with zeroes at the end if needed.
    assert isinstance(data, bytearray)
    acc = 0
    bit = 0
    ret = bytearray()
    max_val = 0x1f
    max_acc = 0xfff
    for b in data:
        acc = ((acc << 8) | b) & max_acc
        bit += 8
        for _ in range(bit // 5):
            bit -= 5
            ret.append((acc >> bit) & max_val)
    if bit:
        pad_bit = 5 - bit
        ret.append((acc << pad_bit) & max_val)
    return ret


def bech32m_re_arrange_8(data: bytearray) -> bytearray:
    # Re-arrange those bits into groups of 8 bits. Any incomplete group at the end MUST be 4 bits or less, MUST be all
    # zeroes, and is discarded.
    assert isinstance(data, bytearray)
    acc = 0
    bit = 0
    ret = bytearray()
    max_val = 0xff
    max_acc = 0xfff
    for b in data:
        assert b <= 0x1f
        acc = ((acc << 5) | b) & max_acc
        bit += 5
        for _ in range(bit // 8):
            bit -= 8
            ret.append((acc >> bit) & max_val)
    assert bit < 5
    return ret


def decode(hrp: str, addr: str) -> typing.Tuple[int, bytearray]:
    # Decode a segwit address.
    hrq, data = bech32m_decode(addr)
    assert hrq == hrp
    ver = data[0]
    assert ver >= 1
    return ver, bech32m_re_arrange_8(data[1:])


def encode(hrp: str, ver: int, prog: bytearray) -> str:
    # Encode a segwit address.
    assert ver >= 1
    assert isinstance(prog, bytearray)
    r = bech32m_encode(hrp, bytearray([ver]) + bech32m_re_arrange_5(prog))
    b = decode(hrp, r)
    assert b[0] == ver
    assert b[1] == prog
    return r
