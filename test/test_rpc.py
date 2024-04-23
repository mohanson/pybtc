import btc


def test_get_block_count():
    btc.config.current = btc.config.develop
    assert btc.rpc.get_block_count() != 0
