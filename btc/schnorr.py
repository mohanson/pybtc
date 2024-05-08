import btc.secp256k1


def sign(prikey: btc.secp256k1.Fr, m: btc.secp256k1.Fr):
    pubkey = btc.secp256k1.G * prikey
    if pubkey.y.x & 1:
        pubkey = -pubkey
    # k = btc.secp256k1.Fr(random.randint(0, secp256k1.N))
    # R = secp256k1.G * k
    # hasher = hashlib.sha256()
    # hasher.update(R.x.x.to_bytes(32, 'little'))
    # hasher.update(R.y.x.to_bytes(32, 'little'))
    # hasher.update(m.x.to_bytes(32, 'little'))
    # e = secp256k1.Fr(int.from_bytes(hasher.digest(), 'little'))
    # s = k + e * prikey
    # return R, s
    pass


def verify():
    pass
