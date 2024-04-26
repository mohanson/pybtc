import btc


def test_generate_to_address():
    btc.config.current = btc.config.develop
    prikey = btc.core.PriKey(1)
    pubkey = prikey.pubkey()
    addr = btc.core.address_p2wpkh(pubkey)
    hash = btc.rpc.generate_to_address(4, addr)
    assert len(hash) == 4


def test_get_best_block_hash():
    btc.config.current = btc.config.develop
    hash = btc.rpc.get_best_block_hash()
    assert len(hash) == 64


def test_get_block_count():
    btc.config.current = btc.config.develop
    assert btc.rpc.get_block_count() != 0
