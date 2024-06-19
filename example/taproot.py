import btc

# This example shows how to create a P2TR script with two unlock conditions: p2pk and p2ms.


# Here created two scripts, one of which is a p2pk script, which requires that it can only be unlocked by private key 2,
# and the other is an 2-of-2 multisig script.
mast = btc.core.TapNode(
    btc.core.TapLeaf(btc.core.script([
        btc.opcode.op_pushdata(btc.core.PriKey(2).pubkey().sec()[1:]),
        btc.opcode.op_checksig,
    ])),
    btc.core.TapLeaf(btc.core.script([
        btc.opcode.op_pushdata(btc.core.PriKey(3).pubkey().sec()[1:]),
        btc.opcode.op_checksig,
        btc.opcode.op_pushdata(btc.core.PriKey(4).pubkey().sec()[1:]),
        btc.opcode.op_checksigadd,
        btc.opcode.op_n(2),
        btc.opcode.op_equal,
    ]))
)


class Tp2trp2pk:
    def __init__(self, pubkey: btc.core.PubKey):
        self.pubkey = pubkey
        self.addr = btc.core.address_p2tr(pubkey, mast.hash)
        self.script = btc.core.script_pubkey_p2tr(self.addr)
        output_pubkey_byte = bytearray([0x02]) + btc.bech32.decode(btc.config.current.prefix.bech32, 1, self.addr)
        output_pubkey = btc.core.PubKey.sec_decode(output_pubkey_byte)
        # Control byte with leaf version and parity bit.
        if output_pubkey.y & 1:
            self.prefix = 0xc1
        else:
            self.prefix = 0xc0

    def sign(self, tx: btc.core.Transaction):
        for i, e in enumerate(tx.vin):
            m = tx.digest_segwit_v1(i, btc.core.sighash_all, mast.l.script)
            s = btc.core.PriKey(2).sign_schnorr(m) + bytearray([btc.core.sighash_all])
            e.witness[0] = s

    def txin(self, op: btc.core.OutPoint):
        return btc.core.TxIn(op, bytearray(), 0xffffffff, [
            bytearray(65),
            mast.l.script,
            bytearray([self.prefix]) + self.pubkey.sec()[1:] + mast.r.hash,
        ])


class Tp2trp2ms:
    def __init__(self, pubkey: btc.core.PubKey):
        self.pubkey = pubkey
        self.addr = btc.core.address_p2tr(pubkey, mast.hash)
        self.script = btc.core.script_pubkey_p2tr(self.addr)
        output_pubkey_byte = bytearray([0x02]) + btc.bech32.decode(btc.config.current.prefix.bech32, 1, self.addr)
        output_pubkey = btc.core.PubKey.sec_decode(output_pubkey_byte)
        # Control byte with leaf version and parity bit.
        if output_pubkey.y & 1:
            self.prefix = 0xc1
        else:
            self.prefix = 0xc0

    def sign(self, tx: btc.core.Transaction):
        for i, e in enumerate(tx.vin):
            m = tx.digest_segwit_v1(i, btc.core.sighash_all, mast.r.script)
            e.witness[0] = btc.core.PriKey(4).sign_schnorr(m) + bytearray([btc.core.sighash_all])
            e.witness[1] = btc.core.PriKey(3).sign_schnorr(m) + bytearray([btc.core.sighash_all])

    def txin(self, op: btc.core.OutPoint):
        return btc.core.TxIn(op, bytearray(), 0xffffffff, [
            bytearray(65),
            bytearray(65),
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
print('main: spending by key path')
user_p2tr.transfer_all(mate.script)
assert user_p2tr.balance() == 0
print('main: spending by key path done')

# Spending by script path: pay to public key.
mate.transfer(user_p2tr.script, 1 * btc.denomination.bitcoin)
assert user_p2tr.balance() == btc.denomination.bitcoin
user_p2pk = btc.wallet.Wallet(Tp2trp2pk(user_p2tr.signer.pubkey))
print('main: spending by script path p2pk')
user_p2pk.transfer_all(mate.script)
assert user_p2tr.balance() == 0
print('main: spending by script path p2pk done')

# Spending by script path: pay to 2-of-2 multisig script.
mate.transfer(user_p2tr.script, 1 * btc.denomination.bitcoin)
assert user_p2tr.balance() == btc.denomination.bitcoin
user_p2ms = btc.wallet.Wallet(Tp2trp2ms(user_p2tr.signer.pubkey))
print('main: spending by script path p2ms')
user_p2ms.transfer_all(mate.script)
assert user_p2tr.balance() == 0
print('main: spending by script path p2ms done')
