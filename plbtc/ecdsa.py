import itertools
import random
import typing
import plbtc.secp256k1



def sign(prikey: plbtc.secp256k1.Fr, m: plbtc.secp256k1.Fr) -> typing.Tuple[plbtc.secp256k1.Fr, plbtc.secp256k1.Fr, int]:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.3 Signing Operation
    for _ in itertools.repeat(0):
        k = plbtc.secp256k1.Fr(random.randint(0, plbtc.secp256k1.N - 1))
        R = plbtc.secp256k1.G * k
        r = plbtc.secp256k1.Fr(R.x.x)
        if r.x == 0:
            continue
        s = (m + prikey * r) / k
        if s.x == 0:
            continue
        v = 0
        if R.y.x & 1 == 1:
            v |= 1
        if R.x.x >= plbtc.secp256k1.N:
            v |= 2
        return r, s, v


def verify(pubkey: plbtc.secp256k1.Pt, m: plbtc.secp256k1.Fr, r: plbtc.secp256k1.Fr, s: plbtc.secp256k1.Fr) -> bool:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.4 Verifying Operation
    u1 = m / s
    u2 = r / s
    x = plbtc.secp256k1.G * u1 + pubkey * u2
    assert x != plbtc.secp256k1.I
    v = plbtc.secp256k1.Fr(x.x.x)
    return v == r


def pubkey(m: plbtc.secp256k1.Fr, r: plbtc.secp256k1.Fr, s: plbtc.secp256k1.Fr, v: int) -> plbtc.secp256k1.Pt:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.6 Public Key Recovery Operation
    assert v in [0, 1, 2, 3]
    if v & 2 == 0:
        x = plbtc.secp256k1.Fq(r.x)
    else:
        x = plbtc.secp256k1.Fq(r.x + plbtc.secp256k1.N)
    y_y = x * x * x + plbtc.secp256k1.A * x + plbtc.secp256k1.B
    y = y_y ** ((plbtc.secp256k1.P + 1) // 4)
    if v & 1 != y.x & 1:
        y = -y
    R = plbtc.secp256k1.Pt(x, y)
    return (R * s - plbtc.secp256k1.G * m) / r
