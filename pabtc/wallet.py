import json
import requests
import typing
import pabtc.core
import pabtc.denomination
import pabtc.opcode
import pabtc.rpc
import pabtc.schnorr
import pabtc.secp256k1

class Analyzer:
    # Analyzer is a simple transaction analyzer to reject transactions that are obviously wrong.
    def __init__(self, tx: pabtc.core.Transaction) -> None:
        self.tx = tx

    def analyze_mining_fee(self) -> None:
        # Make sure the transaction fee is less than 50 satoshi per byte. An excessive fee, also called an absurd fee,
        # is any fee rate that's significantly higher than the amount that fee rate estimators currently expect is
        # necessary to get a transaction confirmed in the next block.
        sender_value = 0
        output_value = 0
        for e in self.tx.vin:
            o = e.out_point.load()
            sender_value += o.value
        for e in self.tx.vout:
            output_value += e.value
        assert sender_value - output_value <= self.tx.vbytes() * 50

    def analyze(self) -> None:
        self.analyze_mining_fee()


class Utxo:
    def __init__(self, out_point: pabtc.core.OutPoint, out: pabtc.core.TxOut) -> None:
        self.out_point = out_point
        self.out = out

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def __eq__(self, other) -> bool:
        return all([
            self.out_point == other.out_point,
            self.out == other.out,
        ])

    def json(self) -> typing.Dict:
        return {
            'out_point': self.out_point.json(),
            'out': self.out.json(),
        }


class SearcherCore:
    # Searcher provides the functionality to list unspent transaction outputs (utxo). To use this implementation, make
    # sure the address you want to query has been imported into your bitcoin core wallet.
    def __init__(self) -> None:
        pass

    def unspent(self, addr: str) -> typing.List[Utxo]:
        r = []
        for e in pabtc.rpc.list_unspent([addr]):
            out_point = pabtc.core.OutPoint(bytearray.fromhex(e['txid'])[::-1], e['vout'])
            script_pubkey = bytearray.fromhex(e['scriptPubKey'])
            amount = e['amount'] * pabtc.denomination.bitcoin
            amount = int(amount.to_integral_exact())
            utxo = Utxo(out_point, pabtc.core.TxOut(amount, script_pubkey))
            r.append(utxo)
        return r


class SearcherMempoolSpace:
    # Searcher provides the functionality to list unspent transaction outputs (utxo). Here we use the public API
    # provided by mempool for querying utxo.
    def __init__(self, net: str) -> None:
        assert net in ['mainnet', 'testnet']
        self.net = net

    def get_url(self, addr: str) -> str:
        if self.net == 'mainnet':
            return f'https://mempool.space/api/address/{addr}/utxo'
        if self.net == 'testnet':
            return f'https://mempool.space/testnet/api/address/{addr}/utxo'
        raise Exception

    def unspent(self, addr: str) -> typing.List[Utxo]:
        r = []
        for e in requests.get(self.get_url(addr)).json():
            out_point = pabtc.core.OutPoint(bytearray.fromhex(e['txid'])[::-1], e['vout'])
            # Mempool's api does not provide script_pubkey, so we have to infer it from the address.
            script_pubkey = pabtc.core.script_pubkey(addr)
            amount = e['value']
            utxo = Utxo(out_point, pabtc.core.TxOut(amount, script_pubkey))
            r.append(utxo)
        return r


class Searcher:
    # Searcher provides the functionality to list unspent transaction outputs (utxo).
    def __init__(self) -> None:
        pass

    def unspent(self, addr: str) -> typing.List[Utxo]:
        if pabtc.config.current == pabtc.config.develop:
            return SearcherCore().unspent(addr)
        if pabtc.config.current == pabtc.config.mainnet:
            return SearcherMempoolSpace('mainnet').unspent(addr)
        if pabtc.config.current == pabtc.config.testnet:
            return SearcherMempoolSpace('testnet').unspent(addr)
        raise Exception


class Tp2pkh:
    def __init__(self, prikey: int) -> None:
        self.prikey = pabtc.core.PriKey(prikey)
        self.pubkey = self.prikey.pubkey()
        self.addr = pabtc.core.address_p2pkh(self.pubkey)
        self.script = pabtc.core.script_pubkey_p2pkh(self.addr)

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'prikey': self.prikey.json(),
            'pubkey': self.pubkey.json(),
            'addr': self.addr,
            'script': self.script.hex(),
        }

    def sign(self, tx: pabtc.core.Transaction) -> None:
        for i, e in enumerate(tx.vin):
            s = self.prikey.sign_ecdsa_der(tx.digest_legacy(i, pabtc.core.sighash_all, e.out_point.load().script_pubkey))
            s.append(pabtc.core.sighash_all)
            e.script_sig = pabtc.core.script([
                pabtc.opcode.op_pushdata(s),
                pabtc.opcode.op_pushdata(self.pubkey.sec())
            ])

    def txin(self, op: pabtc.core.OutPoint) -> pabtc.core.TxIn:
        return pabtc.core.TxIn(op, bytearray(107), 0xffffffff, [])


class Tp2shp2ms:
    # Multi-signature: See https://en.bitcoin.it/wiki/Multi-signature.
    def __init__(self, pubkey: typing.List[pabtc.core.PubKey], prikey: typing.List[int]) -> None:
        self.prikey = [pabtc.core.PriKey(e) for e in prikey]
        self.pubkey = pubkey
        script_asts = []
        script_asts.append(pabtc.opcode.op_n(len(prikey)))
        for e in self.pubkey:
            script_asts.append(pabtc.opcode.op_pushdata(e.sec()))
        script_asts.append(pabtc.opcode.op_n(len(pubkey)))
        script_asts.append(pabtc.opcode.op_checkmultisig)
        self.redeem = pabtc.core.script(script_asts)
        self.addr = pabtc.core.address_p2sh(self.redeem)
        self.script = pabtc.core.script_pubkey_p2sh(self.addr)

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'prikey': [e.json() for e in self.prikey],
            'pubkey': [e.json() for e in self.pubkey],
            'addr': self.addr,
            'script': self.script.hex(),
        }

    def sign(self, tx: pabtc.core.Transaction) -> None:
        for i, e in enumerate(tx.vin):
            script_sig = []
            script_sig.append(pabtc.opcode.op_0)
            for prikey in self.prikey:
                s = prikey.sign_ecdsa_der(tx.digest_legacy(i, pabtc.core.sighash_all, self.redeem))
                s.append(pabtc.core.sighash_all)
                script_sig.append(pabtc.opcode.op_pushdata(s))
            script_sig.append(pabtc.opcode.op_pushdata(self.redeem))
            e.script_sig = pabtc.core.script(script_sig)

    def txin(self, op: pabtc.core.OutPoint) -> pabtc.core.TxIn:
        script_sig = []
        script_sig.append(pabtc.opcode.op_0)
        for _ in range(len(self.prikey)):
            script_sig.append(pabtc.opcode.op_pushdata(bytearray(72)))
        script_sig.append(pabtc.opcode.op_pushdata(self.redeem))
        return pabtc.core.TxIn(op, pabtc.core.script(script_sig), 0xffffffff, [])


class Tp2shp2wpkh:
    def __init__(self, prikey: int) -> None:
        self.prikey = pabtc.core.PriKey(prikey)
        self.pubkey = self.prikey.pubkey()
        self.addr = pabtc.core.address_p2sh_p2wpkh(self.pubkey)
        self.script = pabtc.core.script_pubkey_p2sh(self.addr)

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'prikey': self.prikey.json(),
            'pubkey': self.pubkey.json(),
            'addr': self.addr,
            'script': self.script.hex(),
        }

    def sign(self, tx: pabtc.core.Transaction) -> None:
        # See: https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki#p2wpkh-nested-in-bip16-p2sh
        pubkey_hash = pabtc.core.hash160(self.pubkey.sec())
        script_code = pabtc.core.script([
            pabtc.opcode.op_pushdata(pabtc.core.script([
                pabtc.opcode.op_dup,
                pabtc.opcode.op_hash160,
                pabtc.opcode.op_pushdata(pubkey_hash),
                pabtc.opcode.op_equalverify,
                pabtc.opcode.op_checksig,
            ]))])
        script_sig = pabtc.core.script([pabtc.opcode.op_pushdata(pabtc.core.script([
            pabtc.opcode.op_0,
            pabtc.opcode.op_pushdata(pubkey_hash)
        ]))])
        for i, e in enumerate(tx.vin):
            e.script_sig = script_sig
            s = self.prikey.sign_ecdsa_der(tx.digest_segwit_v0(i, pabtc.core.sighash_all, script_code))
            s.append(pabtc.core.sighash_all)
            e.witness[0] = s
            e.witness[1] = self.pubkey.sec()

    def txin(self, op: pabtc.core.OutPoint) -> pabtc.core.TxIn:
        return pabtc.core.TxIn(op, bytearray(23), 0xffffffff, [bytearray(72), bytearray(33)])


class Tp2wpkh:
    def __init__(self, prikey: int) -> None:
        self.prikey = pabtc.core.PriKey(prikey)
        self.pubkey = self.prikey.pubkey()
        self.addr = pabtc.core.address_p2wpkh(self.pubkey)
        self.script = pabtc.core.script_pubkey_p2wpkh(self.addr)

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'prikey': self.prikey.json(),
            'pubkey': self.pubkey.json(),
            'addr': self.addr,
            'script': self.script.hex(),
        }

    def sign(self, tx: pabtc.core.Transaction) -> None:
        # See: https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki#p2wpkh
        pubkey_hash = pabtc.core.hash160(self.pubkey.sec())
        script_code = pabtc.core.script([
            pabtc.opcode.op_pushdata(pabtc.core.script([
                pabtc.opcode.op_dup,
                pabtc.opcode.op_hash160,
                pabtc.opcode.op_pushdata(pubkey_hash),
                pabtc.opcode.op_equalverify,
                pabtc.opcode.op_checksig,
            ]))])
        for i, e in enumerate(tx.vin):
            s = self.prikey.sign_ecdsa_der(tx.digest_segwit_v0(i, pabtc.core.sighash_all, script_code))
            s.append(pabtc.core.sighash_all)
            e.witness[0] = s
            e.witness[1] = self.pubkey.sec()

    def txin(self, op: pabtc.core.OutPoint) -> pabtc.core.TxIn:
        return pabtc.core.TxIn(op, bytearray(), 0xffffffff, [bytearray(72), bytearray(33)])


class Tp2tr:
    def __init__(self, prikey: int, root: bytearray) -> None:
        self.prikey = pabtc.core.PriKey(prikey)
        self.pubkey = self.prikey.pubkey()
        self.addr = pabtc.core.address_p2tr(self.pubkey, root)
        self.root = root
        self.script = pabtc.core.script_pubkey_p2tr(self.addr)

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'prikey': self.prikey.json(),
            'pubkey': self.pubkey.json(),
            'addr': self.addr,
            'root': self.root.hex(),
            'script': self.script.hex(),
        }

    def sign(self, tx: pabtc.core.Transaction) -> None:
        # See: https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki
        prikey = pabtc.secp256k1.Fr(self.prikey.n)
        adjust_prikey_byte = pabtc.core.hashtag('TapTweak', bytearray(self.pubkey.x.to_bytes(32)) + self.root)
        adjust_prikey = pabtc.secp256k1.Fr(int.from_bytes(adjust_prikey_byte))
        output_prikey = prikey + adjust_prikey
        output_prikey = pabtc.core.PriKey(output_prikey.x)
        for i, e in enumerate(tx.vin):
            m = tx.digest_segwit_v1(i, pabtc.core.sighash_all, bytearray())
            s = output_prikey.sign_schnorr(m) + bytearray([pabtc.core.sighash_all])
            e.witness[0] = s
        return tx

    def txin(self, op: pabtc.core.OutPoint) -> pabtc.core.TxIn:
        return pabtc.core.TxIn(op, bytearray(), 0xffffffff, [bytearray(65)])


T = Tp2pkh | Tp2shp2ms | Tp2shp2wpkh | Tp2wpkh | Tp2tr


class Wallet:
    def __init__(self, signer: T) -> None:
        self.signer = signer
        self.addr = self.signer.addr
        self.script = self.signer.script
        self.search = Searcher()

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def balance(self) -> int:
        return sum([e.out.value for e in self.unspent()])

    def json(self) -> typing.Dict:
        return self.signer.json()

    def transfer(self, script: bytearray, value: int) -> bytearray:
        sender_value = 0
        accept_value = value
        accept_script = script
        change_value = 0
        change_script = self.script
        fr = pabtc.rpc.estimates_mart_fee(6)['feerate'] * pabtc.denomination.bitcoin
        fr = int(fr.to_integral_exact()) // 1000
        tx = pabtc.core.Transaction(2, [], [], 0)
        tx.vout.append(pabtc.core.TxOut(accept_value, accept_script))
        tx.vout.append(pabtc.core.TxOut(change_value, change_script))
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
        txid = bytearray.fromhex(pabtc.rpc.send_raw_transaction(tx.serialize().hex()))[::-1]
        return txid

    def transfer_all(self, script: bytearray) -> bytearray:
        sender_value = 0
        accept_value = 0
        accept_script = script
        fr = pabtc.rpc.estimates_mart_fee(6)['feerate'] * pabtc.denomination.bitcoin
        fr = int(fr.to_integral_exact()) // 1000
        tx = pabtc.core.Transaction(2, [], [], 0)
        tx.vout.append(pabtc.core.TxOut(accept_value, accept_script))
        for utxo in self.unspent():
            txin = self.signer.txin(utxo.out_point)
            tx.vin.append(txin)
            sender_value += utxo.out.value
        accept_value = sender_value - tx.vbytes() * fr
        assert accept_value >= 546
        tx.vout[0].value = accept_value
        self.signer.sign(tx)
        Analyzer(tx).analyze()
        txid = bytearray.fromhex(pabtc.rpc.send_raw_transaction(tx.serialize().hex()))[::-1]
        return txid

    def unspent(self) -> typing.List[Utxo]:
        return self.search.unspent(self.addr)
