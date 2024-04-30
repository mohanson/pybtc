import btc.config
import btc.ripemd160
import hashlib
import io
import json
import typing


def hash160(data: bytearray) -> bytearray:
    return bytearray(btc.ripemd160.ripemd160(hashlib.sha256(data).digest()).digest())


def hash256(data: bytearray) -> bytearray:
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

    def pubkey(self):
        pubkey = btc.secp256k1.G * btc.secp256k1.Fr(self.n)
        return PubKey(pubkey.x.x, pubkey.y.x)

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

# Bitcoin address prefix: https://en.bitcoin.it/wiki/List_of_address_prefixes


def address_p2pkh(pubkey: PubKey) -> str:
    # Legacy
    pubkey_hash = hash160(pubkey.sec())
    version = bytearray([btc.config.current.prefix.p2pkh])
    checksum = hash256(version + pubkey_hash)
    address = btc.base58.encode(version + pubkey_hash + checksum[:4])
    return address


def address_p2sh(pubkey: PubKey) -> str:
    # Nested Segwit.
    # See https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki
    pubkey_hash = hash160(pubkey.sec())
    redeem_hash = hash160(bytearray([0x00, 0x14]) + pubkey_hash)
    version = bytearray([btc.config.current.prefix.p2sh])
    checksum = hash256(version + redeem_hash)
    address = btc.base58.encode(version + redeem_hash + checksum[:4])
    return address


def address_p2wpkh(pubkey: PubKey) -> str:
    # Native SegWit.
    # See https://github.com/bitcoin/bips/blob/master/bip-0084.mediawiki
    pubkey_hash = hash160(pubkey.sec())
    return btc.bech32.encode(btc.config.current.prefix.bech32, 0, pubkey_hash)


def address_p2tr(pubkey: PubKey) -> str:
    # Taproot.
    # See https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki
    if pubkey.y & 1 != 0:
        # Taproot requires that the y coordinate of the public key is even.
        pubkey.y = btc.secp256k1.P - pubkey.y
    tweak_k_data = bytearray([
        0xe8, 0x0f, 0xe1, 0x63, 0x9c, 0x9c, 0xa0, 0x50, 0xe3, 0xaf, 0x1b, 0x39, 0xc1, 0x43, 0xc6, 0x3e,
        0x42, 0x9c, 0xbc, 0xeb, 0x15, 0xd9, 0x40, 0xfb, 0xb5, 0xc5, 0xa1, 0xf4, 0xaf, 0x57, 0xc5, 0xe9,
        0xe8, 0x0f, 0xe1, 0x63, 0x9c, 0x9c, 0xa0, 0x50, 0xe3, 0xaf, 0x1b, 0x39, 0xc1, 0x43, 0xc6, 0x3e,
        0x42, 0x9c, 0xbc, 0xeb, 0x15, 0xd9, 0x40, 0xfb, 0xb5, 0xc5, 0xa1, 0xf4, 0xaf, 0x57, 0xc5, 0xe9
    ])
    tweak_k_data.extend(pubkey.sec()[1:])
    tweak_k = btc.secp256k1.Fr(int.from_bytes(hashlib.sha256(tweak_k_data).digest()))
    tweak_p = btc.secp256k1.G * tweak_k
    tweak_p = btc.secp256k1.Pt(btc.secp256k1.Fq(pubkey.x), btc.secp256k1.Fq(pubkey.y)) + tweak_p
    return btc.bech32m.encode(btc.config.current.prefix.bech32, 1, bytearray(tweak_p.x.x.to_bytes(32)))


def compact_size_encode(n: int) -> bytearray:
    # Integer can be encoded depending on the represented value to save space. Variable length integers always precede
    # an array/vector of a type of data that may vary in length. Longer numbers are encoded in little endian.
    # See: https://en.bitcoin.it/wiki/Protocol_documentation#Variable_length_integer
    assert n >= 0
    assert n <= 0xffffffffffffffff
    if n <= 0xfc:
        return bytearray([n])
    if n <= 0xffff:
        return bytearray([0xfd]) + bytearray(n.to_bytes(2, 'little'))
    if n <= 0xffffffff:
        return bytearray([0xfe]) + bytearray(n.to_bytes(4, 'little'))
    if n <= 0xffffffffffffffff:
        return bytearray([0xff]) + bytearray(n.to_bytes(8, 'little'))
    raise Exception


def compact_size_decode(data: bytearray) -> int:
    head = data[0]
    if head <= 0xfc:
        return head
    if head == 0xfd:
        assert len(data) == 3
    if head == 0xfe:
        assert len(data) == 5
    if head == 0xff:
        assert len(data) == 9
    return int.from_bytes(data[1:], 'little')


def compact_size_decode_reader(reader: typing.BinaryIO) -> int:
    head = reader.read(1)[0]
    if head <= 0xfc:
        return head
    if head == 0xfd:
        return int.from_bytes(reader.read(2), 'little')
    if head == 0xfe:
        return int.from_bytes(reader.read(4), 'little')
    if head == 0xff:
        return int.from_bytes(reader.read(8), 'little')
    raise Exception


class OutPoint:
    def __init__(self, txid: bytearray, vout: int):
        assert len(txid) == 32
        assert vout >= 0
        assert vout <= 0xffffffff
        self.txid = txid
        self.vout = vout

    def __repr__(self):
        return json.dumps(self.json())

    def json(self):
        return {
            'txid': f'0x{self.txid.hex()}',
            'vout': self.vout,
        }


class TxIn:
    def __init__(self, out_point: OutPoint, script_sig: bytearray, sequence: int, witness: bytearray):
        assert sequence >= 0
        assert sequence <= 0xffffffff
        self.out_point = out_point
        self.script_sig = script_sig
        self.sequence = sequence
        self.witness = witness

    def __repr__(self):
        return json.dumps(self.json())

    def json(self):
        return {
            'out_point': self.out_point.json(),
            'script_sig': f'0x{self.script_sig.hex()}',
            'sequence': self.sequence,
            'witness': f'0x{self.witness.hex()}',
        }


class TxOut:
    def __init__(self, value: int, script_pubkey: bytearray):
        assert value >= 0
        assert value <= 0xffffffffffffffff
        self.value = value
        self.script_pubkey = script_pubkey

    def __repr__(self):
        return json.dumps(self.json())

    def json(self):
        return {
            'value': self.value,
            'script_pubkey': f'0x{self.script_pubkey.hex()}',
        }


class Transaction:
    def __init__(self, version: int, vin: typing.List[TxIn], vout: typing.List[TxOut], locktime: int):
        self.version = version
        self.vin = vin
        self.vout = vout
        self.locktime = locktime

    def __repr__(self):
        return json.dumps(self.json())

    def json(self):
        return {
            'version': self.version,
            'vin': [e.json() for e in self.vin],
            'vout': [e.json() for e in self.vout],
            'locktime': self.locktime,
        }

    def serialize(self):
        # BIP-0144 defines new messages and serialization formats for propagation of transactions and blocks committing
        # to segregated witness structures.
        # See: https://github.com/bitcoin/bips/blob/master/bip-0144.mediawiki
        data = bytearray()
        data.extend(bytearray([self.version, 0x00, 0x00, 0x00]))
        data.append(0x00)
        data.append(0x01)
        data.extend(compact_size_encode(len(self.vin)))
        for i in self.vin:
            # Why does bitcoin core print sha256 hashes (uint256) bytes in reverse order?
            # See: https://bitcoin.stackexchange.com/questions/116730
            data.extend(i.out_point.txid[::-1])
            data.extend(i.out_point.vout.to_bytes(4, 'little'))
            data.extend(compact_size_encode(len(i.script_sig)))
            data.extend(i.script_sig)
            data.extend(i.sequence.to_bytes(4, 'little'))
        data.extend(compact_size_encode(len(self.vout)))
        for o in self.vout:
            data.extend(o.value.to_bytes(8, 'little'))
            data.extend(compact_size_encode(len(o.script_pubkey)))
            data.extend(o.script_pubkey)
        data.extend(compact_size_encode(len(self.vin)))
        for i in self.vin:
            data.extend(compact_size_encode(len(i.witness)))
            data.extend(i.witness)
        data.extend(self.locktime.to_bytes(4, 'little'))
        return data

    @staticmethod
    def serialize_read(data: bytearray):
        reader = io.BytesIO(data)
        tx = Transaction(0, [], [], 0)
        tx.version = int.from_bytes(reader.read(4), 'little')
        assert reader.read(1)[0] == 0x00
        assert reader.read(1)[0] == 0x01
        for _ in range(compact_size_decode_reader(reader)):
            txid = bytearray(reader.read(32))[::-1]
            vout = int.from_bytes(reader.read(4), 'little')
            script_sig = bytearray(reader.read(compact_size_decode_reader(reader)))
            sequence = int.from_bytes(reader.read(4), 'little')
            tx.vin.append(TxIn(OutPoint(txid, vout), script_sig, sequence, bytearray()))
        for _ in range(compact_size_decode_reader(reader)):
            value = int.from_bytes(reader.read(8), 'little')
            script_pubkey = bytearray(reader.read(compact_size_decode_reader(reader)))
            tx.vout.append(TxOut(value, script_pubkey))
        for i in range(compact_size_decode_reader(reader)):
            witness = bytearray(reader.read(compact_size_decode_reader(reader)))
            tx.vin[i].witness = witness
        tx.locktime = int.from_bytes(reader.read(4), 'little')
        return tx
