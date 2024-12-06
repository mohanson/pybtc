import plbtc


def test_generate_to_address():
    plbtc.config.current = plbtc.config.develop
    prikey = plbtc.core.PriKey(1)
    pubkey = prikey.pubkey()
    addr = plbtc.core.address_p2wpkh(pubkey)
    hash = plbtc.rpc.generate_to_address(4, addr)
    assert len(hash) == 4


def test_get_best_block_hash():
    plbtc.config.current = plbtc.config.develop
    hash = plbtc.rpc.get_best_block_hash()
    assert len(hash) == 64


def test_get_block_count():
    plbtc.config.current = plbtc.config.develop
    assert plbtc.rpc.get_block_count() != 0
