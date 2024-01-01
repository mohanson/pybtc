import btc.config
import btc.ripemd160
import hashlib
import json


def hash160(data: bytearray) -> bytearray:
    return bytearray(btc.ripemd160.ripemd160(hashlib.sha256(data).digest()))


def hash256(data: bytearray):
    return bytearray(hashlib.sha256(hashlib.sha256(data).digest()).digest())


class PriKey:
    def __init__(self, n: int):
        self.n = n

    def __repr__(self):
        return json.dumps(self.json())

    def __eq__(self, other):
        a = self.n == other.n
        return a

    def json(self):
        return f'0x{self.n:064x}'

    def wif(self):
        # See https://en.bitcoin.it/wiki/Wallet_import_format
        data = bytearray()
        if btc.config.current == btc.config.mainnet:
            data.append(0x80)
        else:
            data.append(0xef)
        data.extend(self.n.to_bytes(32))
        data.append(0x01)
        checksum = hash256(data)[:4]
        data.extend(checksum)
        return btc.base58.encode(data)

    @staticmethod
    def wif_read(data: str):
        data = btc.base58.decode(data)
        if btc.config.current == btc.config.mainnet:
            assert data[0] == 0x80
        else:
            assert data[0] == 0xef
        assert hash256(data[:-4])[:4] == data[-4:]
        return PriKey(int.from_bytes(data[1:33]))

    def pubkey(self):
        pubkey = btc.secp256k1.G * btc.secp256k1.Fr(self.n)
        return PubKey(pubkey.x.x, pubkey.y.x)


class PubKey:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __repr__(self):
        return json.dumps(self.json())

    def __eq__(self, other):
        a = self.x == other.x
        b = self.y == other.y
        return a and b

    def json(self):
        return {
            'x': f'0x{self.x:064x}',
            'y': f'0x{self.y:064x}'
        }

    def sec(self):
        r = bytearray()
        if self.y & 1 == 0:
            r.append(0x02)
        else:
            r.append(0x03)
        r.extend(self.x.to_bytes(32))
        return r

    @staticmethod
    def sec_read(data: bytearray):
        p = data[0]
        assert p in [0x02, 0x03, 0x04]
        x = int.from_bytes(data[1:33])
        if p == 0x04:
            y = int.from_bytes(data[33:65])
        else:
            y_x_y = x * x * x + btc.secp256k1.A.x * x + btc.secp256k1.B.x
            y = pow(y_x_y, (btc.secp256k1.P + 1) // 4, btc.secp256k1.P)
            if y & 1 != p - 2:
                y = -y % btc.secp256k1.P
        return PubKey(x, y)


def address_p2pkh(pubkey: PubKey):
    # Legacy
    pubkey_hash = hash160(pubkey.sec())
    if btc.config.current == btc.config.mainnet:
        version = bytearray([0x00])
    else:
        version = bytearray([0x6f])
    checksum = hash256(version + pubkey_hash)
    address = btc.base58.encode(version + pubkey_hash + checksum[:4])
    return address


def address_p2wpkh(pubkey: PubKey):
    # Native SegWit
    # See https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki
    pubkey_hash = hash160(pubkey.sec())
    if btc.config.current == btc.config.mainnet:
        return btc.bech32.encode('bc', 0, pubkey_hash)
    else:
        return btc.bech32.encode('tb', 0, pubkey_hash)


def address_p2sh(pubkey: PubKey):
    # Nested Segwit
    pubkey_hash = hash160(pubkey.sec())
    redeem_hash = hash160(bytearray([0x00, 0x14]) + pubkey_hash)
    if btc.config.current == btc.config.mainnet:
        version = bytearray([0x05])
    else:
        version = bytearray([0xc4])
    checksum = hash256(version + redeem_hash)
    address = btc.base58.encode(version + redeem_hash + checksum[:4])
    return address


def address_p2tr():
    # Taproot
    pass
