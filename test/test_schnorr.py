import random
import pabtc


def test_schnorr():
    for _ in range(4):
        prikey = pabtc.secp256k1.Fr(random.randint(0, pabtc.secp256k1.N))
        pubkey = pabtc.secp256k1.G * prikey
        m = pabtc.secp256k1.Fr(random.randint(0, pabtc.secp256k1.N))
        r, s = pabtc.schnorr.sign(prikey, m)
        assert pabtc.schnorr.verify(pubkey, m, r, s)
