import yabtc


def test_generate_to_address():
    yabtc.config.current = yabtc.config.develop
    prikey = yabtc.core.PriKey(1)
    pubkey = prikey.pubkey()
    addr = yabtc.core.address_p2wpkh(pubkey)
    hash = yabtc.rpc.generate_to_address(4, addr)
    assert len(hash) == 4


def test_get_best_block_hash():
    yabtc.config.current = yabtc.config.develop
    hash = yabtc.rpc.get_best_block_hash()
    assert len(hash) == 64


def test_get_block_count():
    yabtc.config.current = yabtc.config.develop
    assert yabtc.rpc.get_block_count() != 0
