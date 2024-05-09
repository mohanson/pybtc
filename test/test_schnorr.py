import btc
import random


def test_schnorr():
    for _ in range(4):
        prikey = btc.secp256k1.Fr(random.randint(0, btc.secp256k1.N))
        pubkey = btc.secp256k1.G * prikey
        m = btc.secp256k1.Fr(random.randint(0, btc.secp256k1.N))
        r, s = btc.schnorr.sign(prikey, m)
        assert btc.schnorr.verify(pubkey, m, r, s)
