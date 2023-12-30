import btc


def test_hash160():
    pubkey = bytearray.fromhex('02fb95541bf75e809625f860758a1bc38ac3c1cf120d899096194b94a5e700e891')
    pubkey_hash = btc.core.hash160(pubkey)
    assert pubkey_hash.hex() == '74fe0982ed641b98e94145ee220d2ee3a9693509'
