import random
import plbtc


def test_schnorr():
    for _ in range(4):
        prikey = plbtc.secp256k1.Fr(random.randint(0, plbtc.secp256k1.N))
        pubkey = plbtc.secp256k1.G * prikey
        m = plbtc.secp256k1.Fr(random.randint(0, plbtc.secp256k1.N))
        r, s = plbtc.schnorr.sign(prikey, m)
        assert plbtc.schnorr.verify(pubkey, m, r, s)
