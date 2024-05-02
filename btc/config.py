class ObjectDict(dict):
    def __getattr__(self, name: str):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


develop = ObjectDict({
    'name': 'develop',
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
    'name': 'mainnet',
    'rpc': ObjectDict({
        'addr': 'http://127.0.0.1:8332',
        'username': 'user',
        'password': 'pass',
    }),
    'prefix': ObjectDict({
        'p2pkh': 0x00,
        'p2sh': 0x05,
        'bech32': 'bc',
        'wif': 0x80,
    }),
})

testnet = ObjectDict({
    'name': 'testnet',
    'rpc': ObjectDict({
        'addr': 'http://127.0.0.1:18332',
        'username': 'user',
        'password': 'pass',
    }),
    'prefix': ObjectDict({
        'p2pkh': 0x6f,
        'p2sh': 0xc4,
        'bech32': 'tb',
        'wif': 0xef,
    }),
})

current = develop
