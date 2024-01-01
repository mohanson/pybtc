import btc


def test_hash160():
    pubkey_hash = btc.core.hash160(bytearray([0, 1, 2, 3]))
    assert pubkey_hash.hex() == '3c3fa3d4adcaf8f52d5b1843975e122548269937'


def test_prikey():
    prikey = btc.core.PriKey(1)
    pubkey = prikey.pubkey()
    assert pubkey.x == 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
    assert pubkey.y == 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8


def test_prikey_wif():
    prikey = btc.core.PriKey(1)
    assert prikey.wif() == 'KwDiBf89QgGbjEhKnhXJuH7LrciVrZi3qYjgd9M7rFU73sVHnoWn'
    assert prikey == btc.core.PriKey.wif_read(prikey.wif())


def test_pubkey_sec():
    pubkey = btc.core.PubKey(
        0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
        0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
    )
    assert pubkey.sec().hex() == '0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798'


def test_pubkey_sec_read():
    pubkey = btc.core.PubKey.sec_read(bytes.fromhex(''.join([
        '04',
        '79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798',
        '483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8'
    ])))
    assert pubkey.x == 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
    assert pubkey.y == 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
    pubkey = btc.core.PubKey.sec_read(bytes.fromhex(''.join([
        '02',
        '79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798',
    ])))
    assert pubkey.x == 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
    assert pubkey.y == 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8


def test_address_p2pkh():
    prikey = btc.core.PriKey(1)
    pubkey = prikey.pubkey()
    addr = btc.core.address_p2pkh(pubkey)
    assert addr == '1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH'


def test_address_p2wpkh():
    prikey = btc.core.PriKey(1)
    pubkey = prikey.pubkey()
    addr = btc.core.address_p2wpkh(pubkey)
    assert addr == 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4'


def test_address_p2sh():
    prikey = btc.core.PriKey(1)
    pubkey = prikey.pubkey()
    addr = btc.core.address_p2sh(pubkey)
    assert addr == '3JvL6Ymt8MVWiCNHC7oWU6nLeHNJKLZGLN'


def test_address_p2tr():
    pass
