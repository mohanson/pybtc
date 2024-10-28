import base64
import btc.base58
import btc.bech32
import btc.config
import btc.denomination
import btc.ecdsa
import btc.opcode
import btc.ripemd160
import btc.rpc
import btc.schnorr
import btc.secp256k1
import hashlib
import itertools
import math
import io
import json
import typing

sighash_default = 0x00
sighash_all = 0x01
sighash_none = 0x02
sighash_single = 0x03
sighash_anyone_can_pay = 0x80


def hash160(data: bytearray) -> bytearray:
    return bytearray(btc.ripemd160.ripemd160(hashlib.sha256(data).digest()).digest())


def hash256(data: bytearray) -> bytearray:
    return bytearray(hashlib.sha256(hashlib.sha256(data).digest()).digest())


def hashtag(name: str, data: bytearray) -> bytearray:
    return btc.schnorr.hash(name, data)


class PriKey:
    def __init__(self, n: int) -> None:
        self.n = n

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def __eq__(self, other) -> bool:
        return self.n == other.n

    def json(self) -> typing.Dict:
        return {
            'n': f'0x{self.n:064x}',
        }

    def pubkey(self):
        pubkey = btc.secp256k1.G * btc.secp256k1.Fr(self.n)
        return PubKey(pubkey.x.x, pubkey.y.x)

    def sign_ecdsa(self, data: bytearray) -> typing.Tuple[btc.secp256k1.Fr, btc.secp256k1.Fr, int]:
        assert len(data) == 32
        m = btc.secp256k1.Fr(int.from_bytes(data))
        for _ in itertools.repeat(0):
            r, s, v = btc.ecdsa.sign(btc.secp256k1.Fr(self.n), m)
            # We require that the S value inside ECDSA signatures is at most the curve order divided by 2 (essentially
            # restricting this value to its lower half range).
            # See: https://github.com/bitcoin/bips/blob/master/bip-0146.mediawiki
            if s.x * 2 >= btc.secp256k1.N:
                s = -s
                v ^= 1
            return r, s, v
        raise Exception

    def sign_ecdsa_der(self, data: bytearray) -> bytearray:
        r, s, _ = self.sign_ecdsa(data)
        return der_encode(r, s)

    def sign_schnorr(self, data: bytearray) -> bytearray:
        assert len(data) == 32
        m = btc.secp256k1.Fr(int.from_bytes(data))
        r, s = btc.schnorr.sign(btc.secp256k1.Fr(self.n), m)
        return bytearray(r.x.x.to_bytes(32) + s.x.to_bytes(32))

    def wif(self) -> str:
        # See https://en.bitcoin.it/wiki/Wallet_import_format
        data = bytearray()
        data.append(btc.config.current.prefix.wif)
        data.extend(self.n.to_bytes(32))
        data.append(0x01)
        checksum = hash256(data)[:4]
        data.extend(checksum)
        return btc.base58.encode(data)

    @classmethod
    def wif_decode(cls, data: str) -> typing.Self:
        data = btc.base58.decode(data)
        assert data[0] == btc.config.current.prefix.wif
        assert hash256(data[:-4])[:4] == data[-4:]
        return PriKey(int.from_bytes(data[1:33]))


class PubKey:
    def __init__(self, x: int, y: int) -> None:
        # The public key must be on the curve.
        _ = btc.secp256k1.Pt(btc.secp256k1.Fq(x), btc.secp256k1.Fq(y))
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def __eq__(self, other) -> bool:
        return all([
            self.x == other.x,
            self.y == other.y,
        ])

    def json(self) -> typing.Dict:
        return {
            'x': f'0x{self.x:064x}',
            'y': f'0x{self.y:064x}'
        }

    def pt(self) -> btc.secp256k1.Pt:
        return btc.secp256k1.Pt(btc.secp256k1.Fq(self.x), btc.secp256k1.Fq(self.y))

    @classmethod
    def pt_decode(cls, data: btc.secp256k1.Pt) -> typing.Self:
        return PubKey(data.x.x, data.y.x)

    def sec(self) -> bytearray:
        r = bytearray()
        if self.y & 1 == 0:
            r.append(0x02)
        else:
            r.append(0x03)
        r.extend(self.x.to_bytes(32))
        return r

    @classmethod
    def sec_decode(cls, data: bytearray) -> typing.Self:
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
    data = bytearray([btc.config.current.prefix.p2pkh]) + pubkey_hash
    chk4 = hash256(data)[:4]
    return btc.base58.encode(data + chk4)


def address_p2sh(redeem: bytearray) -> str:
    # Pay to Script Hash.
    # See: https://github.com/bitcoin/bips/blob/master/bip-0016.mediawiki
    redeem_hash = hash160(redeem)
    data = bytearray([btc.config.current.prefix.p2sh]) + redeem_hash
    chk4 = hash256(data)[:4]
    return btc.base58.encode(data + chk4)


def address_p2sh_p2ms(n: int, pubkey: typing.List[PubKey]) -> str:
    redeem_script = []
    redeem_script.append(btc.opcode.op_n(n))
    for e in pubkey:
        redeem_script.append(btc.opcode.op_pushdata(e.sec()))
    redeem_script.append(btc.opcode.op_n(len(pubkey)))
    redeem_script.append(btc.opcode.op_checkmultisig)
    redeem_script = script(redeem_script)
    return address_p2sh(redeem_script)


def address_p2sh_p2wpkh(pubkey: PubKey) -> str:
    # Nested Segwit.
    # See https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki
    pubkey_hash = hash160(pubkey.sec())
    redeem_script = script([btc.opcode.op_0, btc.opcode.op_pushdata(pubkey_hash)])
    return address_p2sh(redeem_script)


def address_p2wpkh(pubkey: PubKey) -> str:
    # Native SegWit.
    # See https://github.com/bitcoin/bips/blob/master/bip-0084.mediawiki
    pubkey_hash = hash160(pubkey.sec())
    return btc.bech32.encode(btc.config.current.prefix.bech32, 0, pubkey_hash)


def address_p2tr(pubkey: PubKey, root: bytearray) -> str:
    # Taproot.
    # See https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki
    origin_pubkey = pubkey.pt()
    if pubkey.y & 1 != 0:
        # Taproot requires that the y coordinate of the public key is even.
        origin_pubkey = -origin_pubkey
    # There is no script path if root is empty.
    assert len(root) in [0x00, 0x20]
    adjust_prikey_byte = hashtag('TapTweak', bytearray(origin_pubkey.x.x.to_bytes(32)) + root)
    adjust_prikey = btc.secp256k1.Fr(int.from_bytes(adjust_prikey_byte))
    adjust_pubkey = btc.secp256k1.G * adjust_prikey
    output_pubkey = origin_pubkey + adjust_pubkey
    return btc.bech32.encode(btc.config.current.prefix.bech32, 1, bytearray(output_pubkey.x.x.to_bytes(32)))


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
    return compact_size_decode_reader(io.BytesIO(data))


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


def difficulty_target(bits: int) -> int:
    assert bits >= 0x00
    assert bits <= 0xffffffff
    base = bits & 0xffffff
    # Since targets are never negative in practice, however, this means the largest legal value for the lower 24 bits
    # is 0x7fffff. Additionally, 0x008000 is the smallest legal value for the lower 24 bits since targets are always
    # stored with the lowest possible exponent.
    assert base >= 0x008000
    assert base <= 0x7fffff
    exps = bits >> 24
    if exps <= 3:
        return base >> (8 * (3 - exps))
    else:
        return base << (8 * (exps - 3))


def difficulty(bits: int) -> float:
    # The formula of difficulty is difficulty_1_target / current_target (target is a 256 bit number).
    # See https://en.bitcoin.it/wiki/Difficulty.
    # The highest possible target (difficulty 1) is defined as 0x1d00ffff.
    return difficulty_target(0x1d00ffff) / difficulty_target(bits)


def difficulty_hash_rate(difficulty: float) -> float:
    # Get network hash rate results in a given difficulty.
    return difficulty * 2**32 / 600


class HashType:
    def __init__(self, n: int) -> None:
        assert n in [
            sighash_default,
            sighash_all,
            sighash_none,
            sighash_single,
            sighash_anyone_can_pay | sighash_all,
            sighash_anyone_can_pay | sighash_none,
            sighash_anyone_can_pay | sighash_single,
        ]
        self.i = n & sighash_anyone_can_pay
        self.o = n & 0x3
        if n == sighash_default:
            self.i = sighash_all


class OutPoint:
    def __init__(self, txid: bytearray, vout: int) -> None:
        assert len(txid) == 32
        assert vout >= 0
        assert vout <= 0xffffffff
        self.txid = txid
        self.vout = vout

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def __eq__(self, other) -> bool:
        return all([
            self.txid == other.txid,
            self.vout == other.vout,
        ])

    def copy(self) -> typing.Self:
        return OutPoint(self.txid.copy(), self.vout)

    def json(self) -> typing.Dict:
        return {
            'txid': f'0x{self.txid.hex()}',
            'vout': self.vout,
        }

    def load(self):
        rpcret = btc.rpc.get_tx_out(self.txid[::-1].hex(), self.vout)
        script_pubkey = bytearray.fromhex(rpcret['scriptPubKey']['hex'])
        amount = rpcret['value'] * btc.denomination.bitcoin
        amount = int(amount.to_integral_exact())
        return TxOut(amount, script_pubkey)


class TxIn:
    def __init__(
        self,
        out_point: OutPoint,
        script_sig: bytearray,
        sequence: int,
        witness: typing.List[bytearray]
    ) -> None:
        assert sequence >= 0
        assert sequence <= 0xffffffff
        self.out_point = out_point
        self.script_sig = script_sig
        self.sequence = sequence
        self.witness = witness

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def __eq__(self, other) -> bool:
        return all([
            self.out_point == other.out_point,
            self.script_sig == other.script_sig,
            self.sequence == other.sequence,
            self.witness == other.witness,
        ])

    def copy(self) -> typing.Self:
        return TxIn(self.out_point.copy(), self.script_sig.copy(), self.sequence, [e.copy() for e in self.witness])

    def json(self) -> typing.Dict:
        return {
            'out_point': self.out_point.json(),
            'script_sig': f'0x{self.script_sig.hex()}',
            'sequence': self.sequence,
            'witness': [f'0x{e.hex()}' for e in self.witness],
        }


class TxOut:
    def __init__(self, value: int, script_pubkey: bytearray) -> None:
        assert value >= 0
        assert value <= 0xffffffffffffffff
        self.value = value
        self.script_pubkey = script_pubkey

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def __eq__(self, other) -> bool:
        return all([
            self.value == other.value,
            self.script_pubkey == other.script_pubkey,
        ])

    def copy(self) -> typing.Self:
        return TxOut(self.value, self.script_pubkey.copy())

    def json(self) -> typing.Dict:
        return {
            'value': self.value,
            'script_pubkey': f'0x{self.script_pubkey.hex()}',
        }


class Transaction:
    # Referring to the design of Bitcoin core.
    # See: https://github.com/bitcoin/bitcoin/blob/master/src/primitives/transaction.h
    def __init__(self, version: int, vin: typing.List[TxIn], vout: typing.List[TxOut], locktime: int) -> None:
        self.version = version
        self.vin = vin
        self.vout = vout
        self.locktime = locktime

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def __eq__(self, other) -> bool:
        return all([
            self.version == other.version,
            self.vin == other.vin,
            self.vout == other.vout,
            self.locktime == other.locktime,
        ])

    def copy(self) -> typing.Self:
        return Transaction(self.version, [i.copy() for i in self.vin], [o.copy() for o in self.vout], self.locktime)

    def digest_legacy(self, i: int, hash_type: int, script_code: bytearray) -> bytearray:
        # The legacy signing algorithm is used to create signatures that will unlock non-segwit locking scripts.
        # See: https://learnmeabitcoin.com/technical/keys/signature/
        ht = HashType(hash_type)
        tx = self.copy()
        for e in tx.vin:
            e.script_sig = bytearray()
        # Put the script_pubkey as a placeholder in the script_sig.
        # If the output is a P2SH output, then we need to use the redeem script.
        tx.vin[i].script_sig = script_code
        if ht.i == sighash_anyone_can_pay:
            tx.vin = [tx.vin[i]]
        if ht.o == sighash_none:
            tx.vout = []
        if ht.o == sighash_single:
            tx.vout = [tx.vout[i]]
        data = tx.serialize_legacy()
        # Append signature hash type to transaction data. The most common is SIGHASH_ALL (0x01), which indicates that
        # the signature covers all of the inputs and outputs in the transaction. This means that nobody else can add
        # any additional inputs or outputs to it later on.
        # The sighash when appended to the transaction data is 4 bytes and in little-endian byte order.
        data.extend(bytearray([hash_type, 0x00, 0x00, 0x00]))
        return hash256(data)

    def digest_segwit_v0(self, i: int, hash_type: int, script_code: bytearray) -> bytearray:
        # A new transaction digest algorithm for signature verification in version 0 witness program, in order to
        # minimize redundant data hashing in verification, and to cover the input value by the signature.
        # See: https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki
        ht = HashType(hash_type)
        data = bytearray()
        # Append version of the transaction.
        data.extend(self.version.to_bytes(4, 'little'))
        # Append hash prevouts.
        hash = bytearray(32)
        if ht.i != sighash_anyone_can_pay:
            snap = bytearray()
            for e in self.vin:
                snap.extend(e.out_point.txid)
                snap.extend(e.out_point.vout.to_bytes(4, 'little'))
            hash = hash256(snap)
        data.extend(hash)
        # Append hash sequence.
        hash = bytearray(32)
        if ht.i != sighash_anyone_can_pay and ht.o == sighash_all:
            snap = bytearray()
            for e in self.vin:
                snap.extend(e.sequence.to_bytes(4, 'little'))
            hash = hash256(snap)
        data.extend(hash)
        # Append outpoint.
        data.extend(self.vin[i].out_point.txid)
        data.extend(self.vin[i].out_point.vout.to_bytes(4, 'little'))
        # Append script code of the input.
        data.extend(script_code)
        # Append value of the output spent by this input.
        data.extend(self.vin[i].out_point.load().value.to_bytes(8, 'little'))
        # Append sequence of the input.
        data.extend(self.vin[i].sequence.to_bytes(4, 'little'))
        # Append hash outputs.
        hash = bytearray(32)
        if ht.o == sighash_all:
            snap = bytearray()
            for e in self.vout:
                snap.extend(e.value.to_bytes(8, 'little'))
                snap.extend(compact_size_encode(len(e.script_pubkey)))
                snap.extend(e.script_pubkey)
            hash = hash256(snap)
        if ht.o == sighash_single and i < len(self.vout):
            snap = bytearray()
            snap.extend(self.vout[i].value.to_bytes(8, 'little'))
            snap.extend(compact_size_encode(len(self.vout[i].script_pubkey)))
            snap.extend(self.vout[i].script_pubkey)
            hash = hash256(snap)
        data.extend(hash)
        # Append locktime of the transaction.
        data.extend(self.locktime.to_bytes(4, 'little'))
        # Append sighash type of the signature.
        data.extend(bytearray([hash_type, 0x00, 0x00, 0x00]))
        return hash256(data)

    def digest_segwit_v1(self, i: int, hash_type: int, script_code: bytearray) -> bytearray:
        # See: https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki#common-signature-message
        ht = HashType(hash_type)
        data = bytearray()
        # This prefix is called the sighash epoch, and allows reusing the hashTapSighash tagged hash in future
        # signature algorithms that make invasive changes to how hashing is performed (as opposed to the ext_flag
        # mechanism that is used for incremental extensions). An alternative is having them use a different tag, but
        # supporting a growing number of tags may become undesirable.
        data.append(0x00)
        data.append(hash_type)
        data.extend(self.version.to_bytes(4, 'little'))
        data.extend(self.locktime.to_bytes(4, 'little'))
        if ht.i != sighash_anyone_can_pay:
            # Append the SHA256 of the serialization of all input outpoints.
            snap = bytearray()
            for e in self.vin:
                snap.extend(e.out_point.txid)
                snap.extend(e.out_point.vout.to_bytes(4, 'little'))
            data.extend(bytearray(hashlib.sha256(snap).digest()))
            # Append the SHA256 of the serialization of all input amounts.
            snap = bytearray()
            for e in self.vin:
                utxo = e.out_point.load()
                snap.extend(utxo.value.to_bytes(8, 'little'))
            data.extend(bytearray(hashlib.sha256(snap).digest()))
            # Append the SHA256 of all spent outputs' scriptPubKeys, serialized as script inside CTxOut.
            snap = bytearray()
            for e in self.vin:
                utxo = e.out_point.load()
                snap.extend(compact_size_encode(len(utxo.script_pubkey)))
                snap.extend(utxo.script_pubkey)
            data.extend(bytearray(hashlib.sha256(snap).digest()))
            # Append the SHA256 of the serialization of all input nSequence.
            snap = bytearray()
            for e in self.vin:
                snap.extend(e.sequence.to_bytes(4, 'little'))
            data.extend(bytearray(hashlib.sha256(snap).digest()))
        if ht.o == sighash_all:
            snap = bytearray()
            for e in self.vout:
                snap.extend(e.value.to_bytes(8, 'little'))
                snap.extend(compact_size_encode(len(e.script_pubkey)))
                snap.extend(e.script_pubkey)
            data.extend(bytearray(hashlib.sha256(snap).digest()))
        spend_type = 0x00
        if script_code:
            spend_type |= 0x2
        data.append(spend_type)
        if ht.i == sighash_anyone_can_pay:
            data.extend(self.vin[i].out_point.txid)
            data.extend(self.vin[i].out_point.vout.to_bytes(4, 'little'))
            utxo = self.vin[i].out_point.load()
            data.extend(utxo.value.to_bytes(8, 'little'))
            data.extend(compact_size_encode(len(utxo.script_pubkey)))
            data.extend(utxo.script_pubkey)
            data.extend(self.vin[i].sequence.to_bytes(4, 'little'))
        if ht.i != sighash_anyone_can_pay:
            data.extend(i.to_bytes(4, 'little'))
        if ht.o == sighash_single:
            snap = bytearray()
            # Using SIGHASH_SINGLE without a "corresponding output" (an output with the same index as the input being
            # verified) cause validation failure.
            snap.extend(self.vout[i].value.to_bytes(8, 'little'))
            snap.extend(compact_size_encode(len(self.vout[i].script_pubkey)))
            snap.extend(self.vout[i].script_pubkey)
            data.extend(bytearray(hashlib.sha256(snap).digest()))
        # See: https://github.com/bitcoin/bips/blob/master/bip-0342.mediawiki
        if script_code:
            snap = bytearray()
            snap.append(0xc0)
            snap.extend(compact_size_encode(len(script_code)))
            snap.extend(script_code)
            data.extend(hashtag('TapLeaf', snap))
            data.append(0x00)
            data.extend(0xffffffff.to_bytes(4, 'little'))
        size = 1 + 174
        if ht.i == sighash_anyone_can_pay:
            size -= 49
        if ht.o == sighash_none:
            size -= 32
        if script_code:
            size += 37
        assert len(data) == size
        return hashtag('TapSighash', data)

    def json(self) -> typing.Dict:
        return {
            'version': self.version,
            'vin': [e.json() for e in self.vin],
            'vout': [e.json() for e in self.vout],
            'locktime': self.locktime,
        }

    def serialize_legacy(self) -> bytearray:
        data = bytearray()
        data.extend(self.version.to_bytes(4, 'little'))
        data.extend(compact_size_encode(len(self.vin)))
        for i in self.vin:
            data.extend(i.out_point.txid)
            data.extend(i.out_point.vout.to_bytes(4, 'little'))
            data.extend(compact_size_encode(len(i.script_sig)))
            data.extend(i.script_sig)
            data.extend(i.sequence.to_bytes(4, 'little'))
        data.extend(compact_size_encode(len(self.vout)))
        for o in self.vout:
            data.extend(o.value.to_bytes(8, 'little'))
            data.extend(compact_size_encode(len(o.script_pubkey)))
            data.extend(o.script_pubkey)
        data.extend(self.locktime.to_bytes(4, 'little'))
        return data

    def serialize_segwit(self) -> bytearray:
        data = bytearray()
        data.extend(self.version.to_bytes(4, 'little'))
        data.append(0x00)
        data.append(0x01)
        data.extend(compact_size_encode(len(self.vin)))
        for i in self.vin:
            data.extend(i.out_point.txid)
            data.extend(i.out_point.vout.to_bytes(4, 'little'))
            data.extend(compact_size_encode(len(i.script_sig)))
            data.extend(i.script_sig)
            data.extend(i.sequence.to_bytes(4, 'little'))
        data.extend(compact_size_encode(len(self.vout)))
        for o in self.vout:
            data.extend(o.value.to_bytes(8, 'little'))
            data.extend(compact_size_encode(len(o.script_pubkey)))
            data.extend(o.script_pubkey)
        for i in self.vin:
            data.extend(witness_encode(i.witness))
        data.extend(self.locktime.to_bytes(4, 'little'))
        return data

    def serialize(self) -> bytearray:
        # If any inputs have nonempty witnesses, the entire transaction is serialized in the BIP141 Segwit format which
        # includes a list of witnesses.
        # See: https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki
        if any([e.witness for e in self.vin]):
            return self.serialize_segwit()
        else:
            return self.serialize_legacy()

    @classmethod
    def serialize_decode_legacy(cls, data: bytearray) -> typing.Self:
        reader = io.BytesIO(data)
        tx = Transaction(0, [], [], 0)
        tx.version = int.from_bytes(reader.read(4), 'little')
        for _ in range(compact_size_decode_reader(reader)):
            txid = bytearray(reader.read(32))
            vout = int.from_bytes(reader.read(4), 'little')
            script_sig = bytearray(reader.read(compact_size_decode_reader(reader)))
            sequence = int.from_bytes(reader.read(4), 'little')
            tx.vin.append(TxIn(OutPoint(txid, vout), script_sig, sequence, []))
        for _ in range(compact_size_decode_reader(reader)):
            value = int.from_bytes(reader.read(8), 'little')
            script_pubkey = bytearray(reader.read(compact_size_decode_reader(reader)))
            tx.vout.append(TxOut(value, script_pubkey))
        tx.locktime = int.from_bytes(reader.read(4), 'little')
        return tx

    @classmethod
    def serialize_decode_segwit(cls, data: bytearray) -> typing.Self:
        reader = io.BytesIO(data)
        tx = Transaction(0, [], [], 0)
        tx.version = int.from_bytes(reader.read(4), 'little')
        assert reader.read(1)[0] == 0x00
        assert reader.read(1)[0] == 0x01
        for _ in range(compact_size_decode_reader(reader)):
            txid = bytearray(reader.read(32))
            vout = int.from_bytes(reader.read(4), 'little')
            script_sig = bytearray(reader.read(compact_size_decode_reader(reader)))
            sequence = int.from_bytes(reader.read(4), 'little')
            tx.vin.append(TxIn(OutPoint(txid, vout), script_sig, sequence, []))
        for _ in range(compact_size_decode_reader(reader)):
            value = int.from_bytes(reader.read(8), 'little')
            script_pubkey = bytearray(reader.read(compact_size_decode_reader(reader)))
            tx.vout.append(TxOut(value, script_pubkey))
        for i in range(len(tx.vin)):
            tx.vin[i].witness = witness_decode_reader(reader)
        tx.locktime = int.from_bytes(reader.read(4), 'little')
        return tx

    @classmethod
    def serialize_decode(cls, data: bytearray) -> typing.Self:
        if data[4] == 0x00:
            return Transaction.serialize_decode_segwit(data)
        else:
            return Transaction.serialize_decode_legacy(data)

    def txid(self) -> bytearray:
        return hash256(self.serialize_legacy())

    def vbytes(self) -> int:
        return math.ceil(self.weight() / 4.0)

    def weight(self) -> int:
        size_legacy = len(self.serialize_legacy())
        size_segwit = len(self.serialize_segwit()) - size_legacy
        return size_legacy * 4 + size_segwit


def script_pubkey_p2pkh(addr: str) -> bytearray:
    data = btc.base58.decode(addr)
    assert data[0] == btc.config.current.prefix.p2pkh
    hash = data[0x01:0x15]
    assert btc.core.hash256(data[0x00:0x15])[:4] == data[0x15:0x19]
    return script([
        btc.opcode.op_dup,
        btc.opcode.op_hash160,
        btc.opcode.op_pushdata(hash),
        btc.opcode.op_equalverify,
        btc.opcode.op_checksig,
    ])


def script_pubkey_p2sh(addr: str) -> bytearray:
    data = btc.base58.decode(addr)
    assert data[0] == btc.config.current.prefix.p2sh
    hash = data[0x01:0x15]
    assert btc.core.hash256(data[0x00:0x15])[:4] == data[0x15:0x19]
    return script([
        btc.opcode.op_hash160,
        btc.opcode.op_pushdata(hash),
        btc.opcode.op_equal,
    ])


def script_pubkey_p2wpkh(addr: str) -> bytearray:
    hash = btc.bech32.decode(btc.config.current.prefix.bech32, 0, addr)
    return script([
        btc.opcode.op_0,
        btc.opcode.op_pushdata(hash),
    ])


def script_pubkey_p2tr(addr: str) -> bytearray:
    pubx = btc.bech32.decode(btc.config.current.prefix.bech32, 1, addr)
    return script([
        btc.opcode.op_1,
        btc.opcode.op_pushdata(pubx),
    ])


def script_pubkey(addr: str) -> bytearray:
    if addr.startswith(btc.config.current.prefix.bech32):
        if addr[len(btc.config.current.prefix.bech32) + 1] == 'q':
            return script_pubkey_p2wpkh(addr)
        if addr[len(btc.config.current.prefix.bech32) + 1] == 'p':
            return script_pubkey_p2tr(addr)
    if btc.base58.decode(addr)[0] == btc.config.current.prefix.p2pkh:
        return script_pubkey_p2pkh(addr)
    if btc.base58.decode(addr)[0] == btc.config.current.prefix.p2sh:
        return script_pubkey_p2sh(addr)
    raise Exception


def script(i: typing.List[int | bytearray]) -> bytearray:
    r = bytearray()
    for e in i:
        if isinstance(e, int):
            r.append(e)
        if isinstance(e, bytearray):
            r.extend(e)
    return r


def der_encode(r: btc.secp256k1.Fr, s: btc.secp256k1.Fr) -> bytearray:
    # DER encoding: https://github.com/bitcoin/bips/blob/master/bip-0062.mediawiki#der-encoding
    body = bytearray()
    body.append(0x02)
    r = r.x.to_bytes(32).lstrip(bytearray([0x00]))
    if r[0] & 0x80:
        r = bytearray([0x00]) + r
    body.append(len(r))
    body.extend(r)
    body.append(0x02)
    s = s.x.to_bytes(32).lstrip(bytearray([0x00]))
    if s[0] & 0x80:
        s = bytearray([0x00]) + s
    body.append(len(s))
    body.extend(s)
    head = bytearray([0x30, len(body)])
    return head + body


def der_decode(sign: bytearray) -> typing.Tuple[btc.secp256k1.Fr, btc.secp256k1.Fr]:
    assert sign[0] == 0x30
    assert sign[1] == len(sign) - 2
    assert sign[2] == 0x02
    rlen = sign[3]
    r = btc.secp256k1.Fr(int.from_bytes(sign[4:4+rlen]))
    f = 4 + rlen
    assert sign[f] == 0x02
    slen = sign[f+1]
    f = f + 2
    s = btc.secp256k1.Fr(int.from_bytes(sign[f:f+slen]))
    return r, s


def witness_encode(wits: typing.List[bytearray]) -> bytearray:
    data = bytearray()
    data.extend(compact_size_encode(len(wits)))
    for e in wits:
        data.extend(compact_size_encode(len(e)))
        data.extend(e)
    return data


def witness_decode(data: bytearray) -> typing.List[bytearray]:
    return witness_decode_reader(io.BytesIO(data))


def witness_decode_reader(r: typing.BinaryIO) -> typing.List[bytearray]:
    wits = []
    for _ in range(compact_size_decode_reader(r)):
        wits.append(bytearray(r.read(compact_size_decode_reader(r))))
    return wits


class Message:
    def __init__(self, data: str) -> None:
        self.data = data

    def hash(self) -> bytearray:
        b = bytearray()
        # Text used to signify that a signed message follows and to prevent inadvertently signing a transaction.
        b.extend(btc.core.compact_size_encode(24))
        b.extend(bytearray('Bitcoin Signed Message:\n'.encode()))
        b.extend(btc.core.compact_size_encode(len(self.data)))
        b.extend(bytearray(self.data.encode()))
        return btc.core.hash256(b)

    def sign(self, prikey: PriKey) -> str:
        r, s, v = prikey.sign_ecdsa(self.hash())
        # Header Byte has the following ranges:
        #   27-30: P2PKH uncompressed
        #   31-34: P2PKH compressed
        #   35-38: Segwit P2SH
        #   39-42: Segwit Bech32
        # See: https://github.com/bitcoin/bips/blob/master/bip-0137.mediawiki.
        sig = bytearray([31 + v]) + bytearray(r.x.to_bytes(32)) + bytearray(s.x.to_bytes(32))
        return base64.b64encode(sig).decode()

    def pubkey(self, sig: str) -> PubKey:
        m = btc.secp256k1.Fr(int.from_bytes(self.hash()))
        sig = base64.b64decode(sig)
        assert sig[0] >= 27
        v = (sig[0] - 27) & 3
        r = btc.secp256k1.Fr(int.from_bytes(sig[0x01:0x21]))
        s = btc.secp256k1.Fr(int.from_bytes(sig[0x21:0x41]))
        return PubKey.pt_decode(btc.ecdsa.pubkey(m, r, s, v))


class TapLeaf:
    def __init__(self, script: bytearray) -> None:
        data = bytearray()
        data.append(0xc0)
        data.extend(compact_size_encode(len(script)))
        data.extend(script)
        self.hash = hashtag('TapLeaf', data)
        self.script = script


class TapNode:
    def __init__(self, l: typing.Self | TapLeaf, r: typing.Self | TapLeaf) -> None:
        if l.hash < r.hash:
            self.hash = hashtag('TapBranch', l.hash + r.hash)
        else:
            self.hash = hashtag('TapBranch', r.hash + l.hash)
        self.l = l
        self.r = r
