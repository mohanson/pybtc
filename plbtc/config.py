import typing


class ObjectDict(dict):
    def __getattr__(self, name: str) -> typing.Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: typing.Any):
        self[name] = value


develop = ObjectDict({
    'rpc': ObjectDict({
        'addr': 'http://127.0.0.1:18443',
        'username': 'user',
        'password': 'pass',
    }),
    'prefix': ObjectDict({
        'p2pkh': 0x6f,
        'p2sh': 0xc4,
        'bech32': 'bcrt',
        'wif': 0xef,
    }),
})

mainnet = ObjectDict({
    'rpc': ObjectDict({
        'addr': 'https://bitcoin.drpc.org/',
        'username': '',
        'password': '',
    }),
    'prefix': ObjectDict({
        'p2pkh': 0x00,
        'p2sh': 0x05,
        'bech32': 'bc',
        'wif': 0x80,
    }),
})

testnet = ObjectDict({
    'rpc': ObjectDict({
        'addr': 'https://bitcoin-testnet.drpc.org/',
        'username': '',
        'password': '',
    }),
    'prefix': ObjectDict({
        'p2pkh': 0x6f,
        'p2sh': 0xc4,
        'bech32': 'tb',
        'wif': 0xef,
    }),
})

current = develop
