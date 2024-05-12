import btc
import json
import typing


class Analyzer:
    # Analyzer is a simple transaction analyzer to reject transactions that are obviously wrong.
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


class Utxo:
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


class Searcher:
    def __init__(self):
        pass

    def unspent(self, addr: str) -> typing.List[Utxo]:
        r = []
        for e in btc.rpc.list_unspent([addr]):
            out_point = btc.core.OutPoint(bytearray.fromhex(e['txid'])[::-1], e['vout'])
            script_pubkey = bytearray.fromhex(e['scriptPubKey'])
            amount = e['amount'] * btc.denomination.bitcoin
            amount = int(amount.to_integral_exact())
            utxo = Utxo(out_point, btc.core.TxOut(amount, script_pubkey))
            r.append(utxo)
        return r


class Tp2pkh:
    def __init__(self, prikey: int):
        self.prikey = btc.core.PriKey(prikey)
        self.pubkey = self.prikey.pubkey()
        self.addr = btc.core.address_p2pkh(self.pubkey)
        self.script = btc.core.script_pubkey_p2pkh(self.addr)

    def __repr__(self):
        return json.dumps(self.json())

    def json(self):
        return {
            'prikey': self.prikey.json(),
            'pubkey': self.pubkey.json(),
            'addr': self.addr,
            'script': self.script.hex(),
        }

    def sign(self, tx: btc.core.Transaction):
        for i, e in enumerate(tx.vin):
            r, s, _ = self.prikey.sign(tx.digest_legacy(i, btc.core.sighash_all, e.out_point.load().script_pubkey))
            g = btc.core.der_encode(r, s) + bytearray([btc.core.sighash_all])
            e.script_sig = btc.core.script([
                btc.opcode.op_pushdata(g),
                btc.opcode.op_pushdata(self.pubkey.sec())
            ])

    def txin(self, op: btc.core.OutPoint):
        return btc.core.TxIn(op, bytearray(107), 0xffffffff, [])


class Tp2shp2ms:
    def __init__(self, prikey: typing.List[int]):
        self.prikey = [btc.core.PriKey(e) for e in prikey]
        self.pubkey = [e.pubkey() for e in self.prikey]
        redeem_script = []
        redeem_script.append(btc.opcode.op_n(len(prikey)))
        for e in self.pubkey:
            redeem_script.append(btc.opcode.op_pushdata(e.sec()))
        redeem_script.append(btc.opcode.op_n(len(prikey)))
        redeem_script.append(btc.opcode.op_checkmultisig)
        self.redeem = btc.core.script(redeem_script)
        self.addr = btc.core.address_p2sh(self.redeem)
        self.script = btc.core.script_pubkey_p2sh(self.addr)

    def __repr__(self):
        return json.dumps(self.json())

    def json(self):
        return {
            'prikey': [e.json() for e in self.prikey],
            'pubkey': [e.json() for e in self.pubkey],
            'addr': self.addr,
            'script': self.script.hex(),
        }

    def sign(self, tx: btc.core.Transaction):
        for i, e in enumerate(tx.vin):
            script_sig = []
            script_sig.append(btc.opcode.op_0)
            for prikey in self.prikey:
                r, s, _ = prikey.sign(tx.digest_legacy(i, btc.core.sighash_all, self.redeem))
                g = btc.core.der_encode(r, s) + bytearray([btc.core.sighash_all])
                script_sig.append(btc.opcode.op_pushdata(g))
            script_sig.append(btc.opcode.op_pushdata(self.redeem))
            e.script_sig = btc.core.script(script_sig)

    def txin(self, op: btc.core.OutPoint):
        script_sig = []
        script_sig.append(btc.opcode.op_0)
        for _ in range(len(self.prikey)):
            script_sig.append(btc.opcode.op_pushdata(bytearray(72)))
        script_sig.append(btc.opcode.op_pushdata(self.redeem))
        return btc.core.TxIn(op, btc.core.script(script_sig), 0xffffffff, [])


class Tp2shp2wpkh:
    def __init__(self, prikey: int):
        self.prikey = btc.core.PriKey(prikey)
        self.pubkey = self.prikey.pubkey()
        self.addr = btc.core.address_p2sh_p2wpkh(self.pubkey)
        self.script = btc.core.script_pubkey_p2sh(self.addr)

    def __repr__(self):
        return json.dumps(self.json())

    def json(self):
        return {
            'prikey': self.prikey.json(),
            'pubkey': self.pubkey.json(),
            'addr': self.addr,
            'script': self.script.hex(),
        }

    def sign(self, tx: btc.core.Transaction):
        # See: https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki#p2wpkh-nested-in-bip16-p2sh
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

    def txin(self, op: btc.core.OutPoint):
        return btc.core.TxIn(op, bytearray(23), 0xffffffff, [bytearray(72), bytearray(33)])


class Tp2wpkh:
    def __init__(self, prikey: int):
        self.prikey = btc.core.PriKey(prikey)
        self.pubkey = self.prikey.pubkey()
        self.addr = btc.core.address_p2wpkh(self.pubkey)
        self.script = btc.core.script_pubkey_p2wpkh(self.addr)

    def __repr__(self):
        return json.dumps(self.json())

    def json(self):
        return {
            'prikey': self.prikey.json(),
            'pubkey': self.pubkey.json(),
            'addr': self.addr,
            'script': self.script.hex(),
        }

    def sign(self, tx: btc.core.Transaction):
        # See: https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki#p2wpkh
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

    def txin(self, op: btc.core.OutPoint):
        return btc.core.TxIn(op, bytearray(), 0xffffffff, [bytearray(72), bytearray(33)])


class Tp2tr:
    def __init__(self, prikey: int):
        self.prikey = btc.core.PriKey(prikey)
        self.pubkey = self.prikey.pubkey()
        self.addr = btc.core.address_p2tr(self.pubkey)
        self.script = btc.core.script_pubkey_p2tr(self.addr)

    def __repr__(self):
        return json.dumps(self.json())

    def json(self):
        return {
            'prikey': self.prikey.json(),
            'pubkey': self.pubkey.json(),
            'addr': self.addr,
            'script': self.script.hex(),
        }

    def sign(self, tx: btc.core.Transaction):
        # See: https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki
        for i, e in enumerate(tx.vin):
            prikey = btc.secp256k1.Fr(self.prikey.n)
            prikey = prikey + btc.secp256k1.Fr(int.from_bytes(btc.core.hashtag('TapTweak', self.pubkey.x.to_bytes(32))))
            m = btc.secp256k1.Fr(int.from_bytes(tx.digest_segwit_v1(i, btc.core.sighash_all)))
            r, s = btc.schnorr.sign(prikey, m)
            e.witness[0] = bytearray(r.x.x.to_bytes(32) + s.x.to_bytes(32)) + bytearray([btc.core.sighash_all])
        return tx

    def txin(self, op: btc.core.OutPoint):
        return btc.core.TxIn(op, bytearray(), 0xffffffff, [bytearray(65)])


T = Tp2pkh | Tp2shp2ms | Tp2shp2wpkh | Tp2wpkh | Tp2tr


class Wallet:
    def __init__(self, signer: T):
        self.signer = signer
        self.addr = self.signer.addr
        self.script = self.signer.script
        self.search = Searcher()

    def __repr__(self):
        return json.dumps(self.json())

    def balance(self):
        return sum([e.out.value for e in self.unspent()])

    def json(self):
        return self.signer.json()

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
            txin = self.signer.txin(utxo.out_point)
            tx.vin.append(txin)
            sender_value += utxo.out.value
            change_value = sender_value - accept_value - tx.vbytes() * fr
            # How was the dust limit of 546 satoshis was chosen?
            # See: https://bitcoin.stackexchange.com/questions/86068
            if change_value >= 546:
                break
        assert change_value >= 546
        tx.vout[1].value = change_value
        self.signer.sign(tx)
        Analyzer(tx).analyze()
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
            txin = self.signer.txin(utxo.out_point)
            tx.vin.append(txin)
            sender_value += utxo.out.value
        accept_value = sender_value - tx.vbytes() * fr
        assert accept_value >= 546
        tx.vout[0].value = accept_value
        self.signer.sign(tx)
        Analyzer(tx).analyze()
        txid = bytearray.fromhex(btc.rpc.send_raw_transaction(tx.serialize().hex()))[::-1]
        return txid

    def unspent(self) -> typing.List[Utxo]:
        return self.search.unspent(self.addr)
