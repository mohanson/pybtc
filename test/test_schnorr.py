import random
import yabtc


def test_schnorr():
    for _ in range(4):
        prikey = yabtc.secp256k1.Fr(random.randint(0, yabtc.secp256k1.N))
        pubkey = yabtc.secp256k1.G * prikey
        m = yabtc.secp256k1.Fr(random.randint(0, yabtc.secp256k1.N))
        r, s = yabtc.schnorr.sign(prikey, m)
        assert yabtc.schnorr.verify(pubkey, m, r, s)
