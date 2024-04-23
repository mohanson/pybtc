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
    })
})

mainnet = ObjectDict({
    'name': 'mainnet',
})

testnet = ObjectDict({
    'name': 'testnet',
})

current = develop
