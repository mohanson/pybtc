import itertools
import random
import typing
import yabtc.secp256k1



def sign(prikey: yabtc.secp256k1.Fr, m: yabtc.secp256k1.Fr) -> typing.Tuple[yabtc.secp256k1.Fr, yabtc.secp256k1.Fr, int]:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.3 Signing Operation
    for _ in itertools.repeat(0):
        k = yabtc.secp256k1.Fr(random.randint(0, yabtc.secp256k1.N - 1))
        R = yabtc.secp256k1.G * k
        r = yabtc.secp256k1.Fr(R.x.x)
        if r.x == 0:
            continue
        s = (m + prikey * r) / k
        if s.x == 0:
            continue
        v = 0
        if R.y.x & 1 == 1:
            v |= 1
        if R.x.x >= yabtc.secp256k1.N:
            v |= 2
        return r, s, v


def verify(pubkey: yabtc.secp256k1.Pt, m: yabtc.secp256k1.Fr, r: yabtc.secp256k1.Fr, s: yabtc.secp256k1.Fr) -> bool:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.4 Verifying Operation
    u1 = m / s
    u2 = r / s
    x = yabtc.secp256k1.G * u1 + pubkey * u2
    assert x != yabtc.secp256k1.I
    v = yabtc.secp256k1.Fr(x.x.x)
    return v == r


def pubkey(m: yabtc.secp256k1.Fr, r: yabtc.secp256k1.Fr, s: yabtc.secp256k1.Fr, v: int) -> yabtc.secp256k1.Pt:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.6 Public Key Recovery Operation
    assert v in [0, 1, 2, 3]
    if v & 2 == 0:
        x = yabtc.secp256k1.Fq(r.x)
    else:
        x = yabtc.secp256k1.Fq(r.x + yabtc.secp256k1.N)
    y_y = x * x * x + yabtc.secp256k1.A * x + yabtc.secp256k1.B
    y = y_y ** ((yabtc.secp256k1.P + 1) // 4)
    if v & 1 != y.x & 1:
        y = -y
    R = yabtc.secp256k1.Pt(x, y)
    return (R * s - yabtc.secp256k1.G * m) / r
