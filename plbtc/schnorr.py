import hashlib
import random
import typing
import plbtc.secp256k1

# Schnorr Signatures for secp256k1.
# See: https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki


def prikey_implicit(prikey: plbtc.secp256k1.Fr) -> plbtc.secp256k1.Fr:
    pubkey = plbtc.secp256k1.G * prikey
    if pubkey == pubkey_implicit(pubkey):
        return +prikey
    else:
        return -prikey


def pubkey_implicit(pubkey: plbtc.secp256k1.Pt) -> plbtc.secp256k1.Pt:
    if pubkey.y.x & 1:
        return -pubkey
    else:
        return +pubkey


def hash(name: str, data: bytearray) -> bytearray:
    tag = bytearray(hashlib.sha256(name.encode()).digest())
    out = bytearray(hashlib.sha256(tag + tag + data).digest())
    return out


def sign(prikey: plbtc.secp256k1.Fr, m: plbtc.secp256k1.Fr) -> typing.Tuple[plbtc.secp256k1.Pt, plbtc.secp256k1.Fr]:
    prikey = prikey_implicit(prikey)
    pubkey = plbtc.secp256k1.G * prikey
    k = prikey_implicit(plbtc.secp256k1.Fr(random.randint(0, plbtc.secp256k1.N)))
    r = plbtc.secp256k1.G * k
    e_data = bytearray(r.x.x.to_bytes(32) + pubkey.x.x.to_bytes(32) + m.x.to_bytes(32))
    e_hash = hash('BIP0340/challenge', e_data)
    e = plbtc.secp256k1.Fr(int.from_bytes(e_hash))
    s = k + e * prikey
    return r, s


def verify(pubkey: plbtc.secp256k1.Pt, m: plbtc.secp256k1.Fr, r: plbtc.secp256k1.Pt, s: plbtc.secp256k1.Fr):
    pubkey = pubkey_implicit(pubkey)
    e_data = bytearray(r.x.x.to_bytes(32) + pubkey.x.x.to_bytes(32) + m.x.to_bytes(32))
    e_hash = hash('BIP0340/challenge', e_data)
    e = plbtc.secp256k1.Fr(int.from_bytes(e_hash))
    return plbtc.secp256k1.G * s == r + pubkey * e
