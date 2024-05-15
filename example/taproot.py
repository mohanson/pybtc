import btc
import typing
Self = typing.Self

# This example shows how to create a P2TR script with two unlock conditions: p2pk and p2as.


class TapLeaf:
    def __init__(self, script: bytearray):
        data = bytearray()
        data.append(0xc0)
        data.extend(btc.core.compact_size_encode(len(script)))
        data.extend(script)
        self.hash = btc.core.hashtag('TapLeaf', data)
        self.script = script


class TapBranch:
    def __init__(self, l: Self | TapLeaf, r: Self | TapLeaf):
        if l.hash < r.hash:
            self.hash = btc.core.hashtag('TapBranch', l.hash + r.hash)
        else:
            self.hash = btc.core.hashtag('TapBranch', r.hash + l.hash)
        self.l = l
        self.r = r


# Here created two scripts, one of which is a p2pk script, which requires that it can only be unlocked by private key 2,
# and the other is an p2as(always success) script, which means that anyone can spend the utxo.
mast = TapBranch(
    TapLeaf(btc.core.script([
        btc.opcode.op_pushdata(btc.core.PriKey(2).pubkey().sec()[1:]),
        btc.opcode.op_checksig,
    ])),
    TapLeaf(btc.core.script([
        btc.opcode.op_1
    ]))
)


class Tp2trp2pk:
    def __init__(self, pubkey: btc.core.PubKey):
        self.pubkey = pubkey
        self.addr = btc.core.address_p2tr(pubkey, mast.hash)
        self.script = btc.core.script_pubkey_p2tr(self.addr)
        output_pubkey_byte = bytearray([0x02]) + btc.bech32.decode(btc.config.current.prefix.bech32, 1, self.addr)
        output_pubkey = btc.core.PubKey.sec_decode(output_pubkey_byte)
        if output_pubkey.y & 1:
            self.prefix = 0xc1
        else:
            self.prefix = 0xc0

    def sign(self, tx: btc.core.Transaction):
        for i, e in enumerate(tx.vin):
            m = btc.secp256k1.Fr(int.from_bytes(tx.digest_segwit_v1(i, btc.core.sighash_all, mast.l.script)))
            r, s = btc.schnorr.sign(btc.secp256k1.Fr(2), m)
            e.witness[0] = bytearray(r.x.x.to_bytes(32) + s.x.to_bytes(32)) + bytearray([btc.core.sighash_all])

    def txin(self, op: btc.core.OutPoint):
        return btc.core.TxIn(op, bytearray(), 0xffffffff, [
            bytearray(65),
            mast.l.script,
            bytearray([self.prefix]) + self.pubkey.x.to_bytes(32) + mast.r.hash,
        ])


class Tp2trp2as:
    def __init__(self, pubkey: btc.core.PubKey):
        self.pubkey = pubkey
        self.addr = btc.core.address_p2tr(pubkey, mast.hash)
        self.script = btc.core.script_pubkey_p2tr(self.addr)
        output_pubkey_byte = bytearray([0x02]) + btc.bech32.decode(btc.config.current.prefix.bech32, 1, self.addr)
        output_pubkey = btc.core.PubKey.sec_decode(output_pubkey_byte)
        if output_pubkey.y & 1:
            self.prefix = 0xc1
        else:
            self.prefix = 0xc0

    def sign(self, tx: btc.core.Transaction):
        return tx

    def txin(self, op: btc.core.OutPoint):
        return btc.core.TxIn(op, bytearray(), 0xffffffff, [
            mast.r.script,
            bytearray([self.prefix]) + self.pubkey.sec()[1:] + mast.l.hash,
        ])


mate = btc.wallet.Wallet(btc.wallet.Tp2pkh(1))
btc.rpc.generate_to_address(10, mate.addr)

user_p2tr = btc.wallet.Wallet(btc.wallet.Tp2tr(1, mast.hash))
btc.rpc.import_descriptors([{
    'desc': btc.rpc.get_descriptor_info(f'addr({user_p2tr.addr})')['descriptor'],
    'timestamp': 'now',
}])

# Spending by key path.
mate.transfer(user_p2tr.script, 1 * btc.denomination.bitcoin)
assert user_p2tr.balance() == btc.denomination.bitcoin
user_p2tr.transfer_all(mate.script)
assert user_p2tr.balance() == 0

# Spending by script path: pay to public key.
mate.transfer(user_p2tr.script, 1 * btc.denomination.bitcoin)
assert user_p2tr.balance() == btc.denomination.bitcoin
user_p2pk = btc.wallet.Wallet(Tp2trp2pk(user_p2tr.signer.pubkey))
user_p2pk.transfer_all(mate.script)
assert user_p2tr.balance() == 0

# Spending by script path: always success(op_1).
mate.transfer(user_p2tr.script, 1 * btc.denomination.bitcoin)
assert user_p2tr.balance() == btc.denomination.bitcoin
user_p2as = btc.wallet.Wallet(Tp2trp2as(user_p2tr.signer.pubkey))
user_p2as.transfer_all(mate.script)
assert user_p2tr.balance() == 0
