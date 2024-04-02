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
})

mainnet = ObjectDict({
    'name': 'mainnet',
})

testnet = ObjectDict({
    'name': 'testnet',
})

current = testnet
