import btc.ripemd160
import hashlib
import json


def hash160(data: bytearray) -> bytearray:
    return bytearray(btc.ripemd160.ripemd160(hashlib.sha256(data).digest()))


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
