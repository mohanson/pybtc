import btc
import json


class Wallet:
    def __init__(self, prikey: int):
        self.prikey = btc.core.PriKey(prikey)
        self.pubkey = self.prikey.pubkey()
        self.addr = btc.core.address_p2pkh(self.pubkey)

    def __repr__(self):
        return json.dumps(self.json())

    def __eq__(self, other):
        return all([
            self.prikey == other.prikey,
            self.pubkey == other.pubkey,
            self.addr == other.addr,
        ])

    def json(self):
        return {
            'prikey': self.prikey.json(),
            'pubkey': self.pubkey.json(),
            'addr': self.addr,
        }
