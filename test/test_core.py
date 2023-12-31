import btc


def test_hash160():
    pubkey_hash = btc.core.hash160(bytearray([0, 1, 2, 3]))
    assert pubkey_hash.hex() == '3c3fa3d4adcaf8f52d5b1843975e122548269937'


def test_prikey():
    prikey = btc.core.PriKey(1)
    pubkey = prikey.pubkey()
    assert pubkey.x == 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
    assert pubkey.y == 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8


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
