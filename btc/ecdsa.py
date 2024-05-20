import btc.secp256k1
import itertools
import random
import typing


def sign(prikey: btc.secp256k1.Fr, m: btc.secp256k1.Fr) -> typing.Tuple[btc.secp256k1.Fr, btc.secp256k1.Fr, int]:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.3 Signing Operation
    for _ in itertools.repeat(0):
        k = btc.secp256k1.Fr(random.randint(0, btc.secp256k1.N - 1))
        R = btc.secp256k1.G * k
        r = btc.secp256k1.Fr(R.x.x)
        if r.x == 0:
            continue
        s = (m + prikey * r) / k
        if s.x == 0:
            continue
        v = 0
        if R.y.x & 1 == 1:
            v |= 1
        if R.x.x >= btc.secp256k1.N:
            v |= 2
        return r, s, v


def verify(pubkey: btc.secp256k1.Pt, m: btc.secp256k1.Fr, r: btc.secp256k1.Fr, s: btc.secp256k1.Fr) -> bool:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.4 Verifying Operation
    u1 = m / s
    u2 = r / s
    x = btc.secp256k1.G * u1 + pubkey * u2
    assert x != btc.secp256k1.I
    v = btc.secp256k1.Fr(x.x.x)
    return v == r


def pubkey(m: btc.secp256k1.Fr, r: btc.secp256k1.Fr, s: btc.secp256k1.Fr, v: int) -> btc.secp256k1.Pt:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.6 Public Key Recovery Operation
    assert v in [0, 1, 2, 3]
    if v & 2 == 0:
        x = btc.secp256k1.Fq(r.x)
    else:
        x = btc.secp256k1.Fq(r.x + btc.secp256k1.N)
    y_y = x * x * x + btc.secp256k1.A * x + btc.secp256k1.B
    y = y_y ** ((btc.secp256k1.P + 1) // 4)
    if v & 1 != y.x & 1:
        y = -y
    R = btc.secp256k1.Pt(x, y)
    return (R * s - btc.secp256k1.G * m) / r
