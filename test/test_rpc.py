import pabtc


def test_generate_to_address():
    pabtc.config.current = pabtc.config.develop
    prikey = pabtc.core.PriKey(1)
    pubkey = prikey.pubkey()
    addr = pabtc.core.address_p2wpkh(pubkey)
    hash = pabtc.rpc.generate_to_address(4, addr)
    assert len(hash) == 4


def test_get_best_block_hash():
    pabtc.config.current = pabtc.config.develop
    hash = pabtc.rpc.get_best_block_hash()
    assert len(hash) == 64


def test_get_block_count():
    pabtc.config.current = pabtc.config.develop
    assert pabtc.rpc.get_block_count() != 0
