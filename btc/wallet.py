import btc
import json
import typing


class WalletUtxo:
    def __init__(self, out_point: btc.core.OutPoint, value: int):
        self.out_point = out_point
        self.value = value

    def __repr__(self):
        return json.dumps(self.json())

    def __eq__(self, other):
        return all([
            self.out_point == other.out_point,
            self.value == other.value,
        ])

    def json(self):
        return {
            'out_point': self.out_point.json(),
            'value': self.value,
        }


class WalletUtxoSearchFromBitcoinCore:
    def __init__(self):
        pass

    def unspent(self, addr: str) -> typing.List[WalletUtxo]:
        r = []
        for e in btc.rpc.list_unspent([addr]):
            out_point = btc.core.OutPoint(bytearray.fromhex(e['txid'])[::-1], e['vout'])
            value = e['amount'] * btc.denomination.bitcoin
            value = int(value.to_integral_exact())
            wallet_utxo = WalletUtxo(out_point, value)
            r.append(wallet_utxo)
        return r


class Wallet:
    def __init__(self, prikey: int):
        self.prikey = btc.core.PriKey(prikey)
        self.pubkey = self.prikey.pubkey()
        self.addr = btc.core.address_p2pkh(self.pubkey)
        self.script = btc.core.script_pubkey_p2pkh(self.addr)
        self.utxo = WalletUtxoSearchFromBitcoinCore()

    def __repr__(self):
        return json.dumps(self.json())

    def __eq__(self, other):
        return all([
            self.prikey == other.prikey,
            self.pubkey == other.pubkey,
            self.addr == other.addr,
        ])

    def balance(self):
        return sum([e.value for e in self.unspent()])

    def json(self):
        return {
            'prikey': self.prikey.json(),
            'pubkey': self.pubkey.json(),
            'addr': self.addr,
        }

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
            tx.vin.append(btc.core.TxIn(utxo.out_point, bytearray(107), 0xffffffff, bytearray()))
            sender_value += utxo.value
            change_value = sender_value - accept_value - tx.vbytes() * fr
            # How was the dust limit of 546 satoshis was chosen?
            # See: https://bitcoin.stackexchange.com/questions/86068
            if change_value >= 546:
                break
        assert change_value >= 546
        tx.vout[1].value = change_value
        for i, e in enumerate(tx.vin):
            r, s, _ = self.prikey.sign(tx.digest_legacy(i, btc.core.sighash_all))
            g = btc.core.der_encode(r, s) + bytearray([btc.core.sighash_all])
            e.script_sig = bytearray([len(g)]) + g + bytearray([33]) + self.pubkey.sec()
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
            tx.vin.append(btc.core.TxIn(utxo.out_point, bytearray(107), 0xffffffff, bytearray()))
            sender_value += utxo.value
        accept_value = sender_value - tx.vbytes() * fr
        assert accept_value >= 546
        tx.vout[0].value = accept_value
        for i, e in enumerate(tx.vin):
            r, s, _ = self.prikey.sign(tx.digest_legacy(i, btc.core.sighash_all))
            g = btc.core.der_encode(r, s) + bytearray([btc.core.sighash_all])
            e.script_sig = bytearray([len(g)]) + g + bytearray([33]) + self.pubkey.sec()
        txid = bytearray.fromhex(btc.rpc.send_raw_transaction(tx.serialize().hex()))[::-1]
        return txid

    def unspent(self) -> typing.List[WalletUtxo]:
        return self.utxo.unspent(self.addr)


class WalletSegwit:
    def __init__(self, prikey: int):
        self.prikey = btc.core.PriKey(prikey)
        self.pubkey = self.prikey.pubkey()
        self.addr = btc.core.address_p2wpkh(self.pubkey)
        self.script = btc.core.script_pubkey_p2wpkh(self.addr)
        self.utxo = WalletUtxoSearchFromBitcoinCore()

    def __repr__(self):
        return json.dumps(self.json())

    def __eq__(self, other):
        return all([
            self.prikey == other.prikey,
            self.pubkey == other.pubkey,
            self.addr == other.addr,
        ])

    def balance(self):
        return sum([e.value for e in self.unspent()])

    def json(self):
        return {
            'prikey': self.prikey.json(),
            'pubkey': self.pubkey.json(),
            'addr': self.addr,
        }

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
            tx.vin.append(btc.core.TxIn(utxo.out_point, bytearray(), 0xffffffff, bytearray(108)))
            sender_value += utxo.value
            change_value = sender_value - accept_value - tx.vbytes() * fr
            # How was the dust limit of 546 satoshis was chosen?
            # See: https://bitcoin.stackexchange.com/questions/86068
            if change_value >= 546:
                break
        assert change_value >= 546
        tx.vout[1].value = change_value
        for i, e in enumerate(tx.vin):
            r, s, _ = self.prikey.sign(tx.digest_segwit(i, btc.core.sighash_all))
            g = btc.core.der_encode(r, s) + bytearray([btc.core.sighash_all])
            buff = bytearray()
            buff.extend(btc.core.compact_size_encode(2))
            buff.extend(btc.core.compact_size_encode(len(g)))
            buff.extend(g)
            buff.extend(btc.core.compact_size_encode(33))
            buff.extend(self.pubkey.sec())
            e.witness = buff
        txid = bytearray.fromhex(btc.rpc.send_raw_transaction(tx.serialize().hex()))[::-1]
        return txid

    def unspent(self) -> typing.List[WalletUtxo]:
        return self.utxo.unspent(self.addr)
