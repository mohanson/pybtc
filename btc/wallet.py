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
            out_point = btc.core.OutPoint(bytearray.fromhex(e['txid']), e['vout'])
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

    def unspent(self) -> typing.List[WalletUtxo]:
        return self.utxo.unspent(self.addr)
