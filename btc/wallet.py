import btc
import json
import typing


class WalletTransactionAnalyzer:
    def __init__(self, tx: btc.core.Transaction):
        self.tx = tx

    def analyze_mining_fee(self):
        # Make sure the transaction fee is less than 50 satoshi per byte. This is a rough check, but works well in most
        # cases.
        sender_value = 0
        output_value = 0
        for e in self.tx.vin:
            o = e.out_point.load()
            sender_value += o.value
        for e in self.tx.vout:
            output_value += e.value
        assert sender_value - output_value <= self.tx.vbytes() * 50

    def analyze(self):
        self.analyze_mining_fee()


class WalletUtxo:
    def __init__(self, out_point: btc.core.OutPoint, out: btc.core.TxOut):
        self.out_point = out_point
        self.out = out

    def __repr__(self):
        return json.dumps(self.json())

    def __eq__(self, other):
        return all([
            self.out_point == other.out_point,
            self.out == other.out,
        ])

    def json(self):
        return {
            'out_point': self.out_point.json(),
            'out': self.out.json(),
        }


class WalletUtxoSearchFromBitcoinCore:
    def __init__(self):
        pass

    def unspent(self, addr: str) -> typing.List[WalletUtxo]:
        r = []
        for e in btc.rpc.list_unspent([addr]):
            out_point = btc.core.OutPoint(bytearray.fromhex(e['txid'])[::-1], e['vout'])
            script_pubkey = bytearray.fromhex(e['scriptPubKey'])
            amount = e['amount'] * btc.denomination.bitcoin
            amount = int(amount.to_integral_exact())
            out = btc.core.TxOut(amount, script_pubkey)
            wallet_utxo = WalletUtxo(out_point, out)
            r.append(wallet_utxo)
        return r


class Wallet:
    def __init__(self, prikey: int, script_type: int):
        assert script_type in [
            btc.core.script_type_p2pkh,
            btc.core.script_type_p2sh,
            btc.core.script_type_p2wpkh,
            btc.core.script_type_p2tr,
        ]
        self.prikey = btc.core.PriKey(prikey)
        self.pubkey = self.prikey.pubkey()
        self.addr = btc.core.address(self.pubkey, script_type)
        self.script_type = script_type
        self.script = btc.core.script_pubkey(self.addr)
        self.utxo = WalletUtxoSearchFromBitcoinCore()

    def __repr__(self):
        return json.dumps(self.json())

    def __eq__(self, other):
        return all([
            self.prikey == other.prikey,
            self.pubkey == other.pubkey,
            self.addr == other.addr,
            self.script_type == other.script_type,
            self.script == other.script,
        ])

    def balance(self):
        return sum([e.out.value for e in self.unspent()])

    def json(self):
        return {
            'prikey': self.prikey.json(),
            'pubkey': self.pubkey.json(),
            'addr': self.addr,
            'script_type': {
                btc.core.script_type_p2pkh: 'p2pkh',
                btc.core.script_type_p2sh: 'p2sh',
                btc.core.script_type_p2wpkh: 'p2wpkh',
                btc.core.script_type_p2tr: 'p2tr',
            }[self.script_type],
            'script': self.script.hex(),
        }

    def sign_p2pkh(self, tx: btc.core.Transaction):
        assert self.script_type == btc.core.script_type_p2pkh
        for i, e in enumerate(tx.vin):
            r, s, _ = self.prikey.sign(tx.digest_legacy(i, btc.core.sighash_all))
            g = btc.core.der_encode(r, s) + bytearray([btc.core.sighash_all])
            e.script_sig = btc.core.script([
                btc.opcode.op_pushdata(g),
                btc.opcode.op_pushdata(self.pubkey.sec())
            ])
        return tx

    def sign_p2sh(self, tx: btc.core.Transaction):
        # See: https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki#p2wpkh-nested-in-bip16-p2sh
        assert self.script_type == btc.core.script_type_p2sh
        pubkey_hash = btc.core.hash160(self.pubkey.sec())
        script_code = btc.core.script([
            btc.opcode.op_pushdata(btc.core.script([
                btc.opcode.op_dup,
                btc.opcode.op_hash160,
                btc.opcode.op_pushdata(pubkey_hash),
                btc.opcode.op_equalverify,
                btc.opcode.op_checksig,
            ]))])
        script_sig = btc.core.script([btc.opcode.op_pushdata(btc.core.script([
            btc.opcode.op_0,
            btc.opcode.op_pushdata(pubkey_hash)
        ]))])
        for i, e in enumerate(tx.vin):
            e.script_sig = script_sig
            r, s, _ = self.prikey.sign(tx.digest_segwit_v0(i, btc.core.sighash_all, script_code))
            g = btc.core.der_encode(r, s) + bytearray([btc.core.sighash_all])
            e.witness[0] = g
            e.witness[1] = self.pubkey.sec()
        return tx

    def sign_p2wpkh(self, tx: btc.core.Transaction):
        # See: https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki#p2wpkh
        assert self.script_type == btc.core.script_type_p2wpkh
        pubkey_hash = btc.core.hash160(self.pubkey.sec())
        script_code = btc.core.script([
            btc.opcode.op_pushdata(btc.core.script([
                btc.opcode.op_dup,
                btc.opcode.op_hash160,
                btc.opcode.op_pushdata(pubkey_hash),
                btc.opcode.op_equalverify,
                btc.opcode.op_checksig,
            ]))])
        for i, e in enumerate(tx.vin):
            r, s, _ = self.prikey.sign(tx.digest_segwit_v0(i, btc.core.sighash_all, script_code))
            g = btc.core.der_encode(r, s) + bytearray([btc.core.sighash_all])
            e.witness[0] = g
            e.witness[1] = self.pubkey.sec()
        return tx

    def sign_p2tr(self, tx: btc.core.Transaction):
        # See: https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki
        assert self.script_type == btc.core.script_type_p2tr
        for i, e in enumerate(tx.vin):
            prikey = btc.secp256k1.Fr(self.prikey.n)
            prikey = prikey + btc.secp256k1.Fr(int.from_bytes(btc.core.hashtag('TapTweak', self.pubkey.x.to_bytes(32))))
            m = btc.secp256k1.Fr(int.from_bytes(tx.digest_segwit_v1(i, btc.core.sighash_all)))
            r, s = btc.schnorr.sign(prikey, m)
            e.witness[0] = bytearray(r.x.x.to_bytes(32) + s.x.to_bytes(32)) + bytearray([btc.core.sighash_all])
        return tx

    def transfer(self, script: bytearray, value: int):
        sender_value = 0
        accept_value = value
        accept_script = script
        change_value = 0
        change_script = self.script
        fr = btc.rpc.estimates_mart_fee(6)['feerate'] * btc.denomination.bitcoin
        fr = int(fr.to_integral_exact()) // 1000
        tx = btc.core.Transaction(2, [], [], 0)
        tx.vout.append(btc.core.TxOut(accept_value, accept_script))
        tx.vout.append(btc.core.TxOut(change_value, change_script))
        for utxo in self.unspent():
            txin = btc.core.TxIn(utxo.out_point, bytearray(), 0xffffffff, [])
            if self.script_type == btc.core.script_type_p2pkh:
                txin.script_sig = bytearray(107)
            if self.script_type == btc.core.script_type_p2sh:
                txin.script_sig = bytearray(23)
                txin.witness = [bytearray(72), bytearray(33)]
            if self.script_type == btc.core.script_type_p2wpkh:
                txin.witness = [bytearray(72), bytearray(33)]
            if self.script_type == btc.core.script_type_p2tr:
                txin.witness = [bytearray(65)]
            tx.vin.append(txin)
            sender_value += utxo.out.value
            change_value = sender_value - accept_value - tx.vbytes() * fr
            # How was the dust limit of 546 satoshis was chosen?
            # See: https://bitcoin.stackexchange.com/questions/86068
            if change_value >= 546:
                break
        assert change_value >= 546
        tx.vout[1].value = change_value
        if self.script_type == btc.core.script_type_p2pkh:
            self.sign_p2pkh(tx)
        if self.script_type == btc.core.script_type_p2sh:
            self.sign_p2sh(tx)
        if self.script_type == btc.core.script_type_p2wpkh:
            self.sign_p2wpkh(tx)
        if self.script_type == btc.core.script_type_p2tr:
            self.sign_p2tr(tx)
        WalletTransactionAnalyzer(tx).analyze()
        txid = bytearray.fromhex(btc.rpc.send_raw_transaction(tx.serialize().hex()))[::-1]
        return txid

    def transfer_all(self, script: bytearray):
        sender_value = 0
        accept_value = 0
        accept_script = script
        fr = btc.rpc.estimates_mart_fee(6)['feerate'] * btc.denomination.bitcoin
        fr = int(fr.to_integral_exact()) // 1000
        tx = btc.core.Transaction(2, [], [], 0)
        tx.vout.append(btc.core.TxOut(accept_value, accept_script))
        for utxo in self.unspent():
            txin = btc.core.TxIn(utxo.out_point, bytearray(), 0xffffffff, [])
            if self.script_type == btc.core.script_type_p2pkh:
                txin.script_sig = bytearray(107)
            if self.script_type == btc.core.script_type_p2sh:
                txin.script_sig = bytearray(23)
                txin.witness = [bytearray(72), bytearray(33)]
            if self.script_type == btc.core.script_type_p2wpkh:
                txin.witness = [bytearray(72), bytearray(33)]
            if self.script_type == btc.core.script_type_p2tr:
                txin.witness = [bytearray(65)]
            tx.vin.append(txin)
            sender_value += utxo.out.value
        accept_value = sender_value - tx.vbytes() * fr
        assert accept_value >= 546
        tx.vout[0].value = accept_value
        if self.script_type == btc.core.script_type_p2pkh:
            self.sign_p2pkh(tx)
        if self.script_type == btc.core.script_type_p2sh:
            self.sign_p2sh(tx)
        if self.script_type == btc.core.script_type_p2wpkh:
            self.sign_p2wpkh(tx)
        if self.script_type == btc.core.script_type_p2tr:
            self.sign_p2tr(tx)
        WalletTransactionAnalyzer(tx).analyze()
        txid = bytearray.fromhex(btc.rpc.send_raw_transaction(tx.serialize().hex()))[::-1]
        return txid

    def unspent(self) -> typing.List[WalletUtxo]:
        return self.utxo.unspent(self.addr)
