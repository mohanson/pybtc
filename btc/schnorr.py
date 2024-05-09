import btc.core
import btc.secp256k1
import random
import typing

# Schnorr Signatures for secp256k1.
# See: https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki


def prikey_implicit(prikey: btc.secp256k1.Fr) -> btc.secp256k1.Fr:
    pubkey = btc.secp256k1.G * prikey
    if pubkey == pubkey_implicit(pubkey):
        return +prikey
    else:
        return -prikey


def pubkey_implicit(pubkey: btc.secp256k1.Pt) -> btc.secp256k1.Pt:
    if pubkey.y.x & 1:
        return -pubkey
    else:
        return +pubkey


def sign(prikey: btc.secp256k1.Fr, m: btc.secp256k1.Fr) -> typing.Tuple[btc.secp256k1.Pt, btc.secp256k1.Fr]:
    prikey = prikey_implicit(prikey)
    pubkey = btc.secp256k1.G * prikey
    k = prikey_implicit(btc.secp256k1.Fr(random.randint(0, btc.secp256k1.N)))
    r = btc.secp256k1.G * k
    e_hash = btc.core.hashtag('challenge', r.x.x.to_bytes(32) + pubkey.x.x.to_bytes(32) + m.x.to_bytes(32))
    e = btc.secp256k1.Fr(int.from_bytes(e_hash))
    s = k + e * prikey
    return r, s


def verify(pubkey: btc.secp256k1.Pt, m: btc.secp256k1.Fr, r: btc.secp256k1.Pt, s: btc.secp256k1.Fr):
    pubkey = pubkey_implicit(pubkey)
    e_hash = btc.core.hashtag('challenge', r.x.x.to_bytes(32) + pubkey.x.x.to_bytes(32) + m.x.to_bytes(32))
    e = btc.secp256k1.Fr(int.from_bytes(e_hash))
    return btc.secp256k1.G * s == r + pubkey * e
