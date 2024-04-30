import btc


def test_hash160():
    hash = btc.core.hash160(bytearray([0, 1, 2, 3]))
    assert hash.hex() == '3c3fa3d4adcaf8f52d5b1843975e122548269937'


def test_prikey():
    prikey = btc.core.PriKey(1)
    pubkey = prikey.pubkey()
    assert pubkey.x == 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
    assert pubkey.y == 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8


def test_prikey_wif():
    btc.config.current = btc.config.mainnet
    prikey = btc.core.PriKey(1)
    assert prikey.wif() == 'KwDiBf89QgGbjEhKnhXJuH7LrciVrZi3qYjgd9M7rFU73sVHnoWn'
    assert prikey == btc.core.PriKey.wif_read(prikey.wif())
    btc.config.current = btc.config.testnet
    assert prikey.wif() == 'cMahea7zqjxrtgAbB7LSGbcQUr1uX1ojuat9jZodMN87JcbXMTcA'
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
    btc.config.current = btc.config.mainnet
    prikey = btc.core.PriKey(1)
    pubkey = prikey.pubkey()
    addr = btc.core.address_p2pkh(pubkey)
    assert addr == '1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH'
    btc.config.current = btc.config.testnet
    addr = btc.core.address_p2pkh(pubkey)
    assert addr == 'mrCDrCybB6J1vRfbwM5hemdJz73FwDBC8r'


def test_address_p2sh():
    btc.config.current = btc.config.mainnet
    prikey = btc.core.PriKey(1)
    pubkey = prikey.pubkey()
    addr = btc.core.address_p2sh(pubkey)
    assert addr == '3JvL6Ymt8MVWiCNHC7oWU6nLeHNJKLZGLN'
    btc.config.current = btc.config.testnet
    addr = btc.core.address_p2sh(pubkey)
    assert addr == '2NAUYAHhujozruyzpsFRP63mbrdaU5wnEpN'


def test_address_p2wpkh():
    btc.config.current = btc.config.mainnet
    prikey = btc.core.PriKey(1)
    pubkey = prikey.pubkey()
    addr = btc.core.address_p2wpkh(pubkey)
    assert addr == 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4'
    btc.config.current = btc.config.testnet
    addr = btc.core.address_p2wpkh(pubkey)
    assert addr == 'tb1qw508d6qejxtdg4y5r3zarvary0c5xw7kxpjzsx'


def test_address_p2tr():
    btc.config.current = btc.config.mainnet
    prikey = btc.core.PriKey(1)
    pubkey = prikey.pubkey()
    addr = btc.core.address_p2tr(pubkey)
    assert addr == 'bc1pmfr3p9j00pfxjh0zmgp99y8zftmd3s5pmedqhyptwy6lm87hf5sspknck9'
    btc.config.current = btc.config.testnet
    addr = btc.core.address_p2tr(pubkey)
    assert addr == 'tb1pmfr3p9j00pfxjh0zmgp99y8zftmd3s5pmedqhyptwy6lm87hf5ssk79hv2'


def test_compact_size():
    for n, b in [
        [0xbb, bytearray([0xbb])],
        [0xff, bytearray([0xfd, 0xff, 0x00])],
        [0x3419, bytearray([0xfd, 0x19, 0x34])],
        [0xdc4591, bytearray([0xfe, 0x91, 0x45, 0xdc, 00])],
        [0x80081e5, bytearray([0xfe, 0xe5, 0x81, 0x00, 0x08])],
        [0xb4da564e2857, bytearray([0xff, 0x57, 0x28, 0x4e, 0x56, 0xda, 0xb4, 0x00, 0x00])],
        [0x4bf583a17d59c158, bytearray([0xff, 0x58, 0xc1, 0x59, 0x7d, 0xa1, 0x83, 0xf5, 0x4b])],
    ]:
        assert btc.core.compact_size_encode(n) == b
        assert btc.core.compact_size_decode(b) == n


def test_transaction():
    # Data copied from mastering bitcoin, chapter 6, example 1, alice's serialized transaction.
    # See: https://github.com/bitcoinbook/bitcoinbook/blob/develop/ch06_transactions.adoc
    data = bytearray([
        0x01, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 0xeb, 0x3a, 0xe3, 0x8f, 0x27, 0x19, 0x1a, 0xa5, 0xf3,
        0x85, 0x0d, 0xc9, 0xca, 0xd0, 0x04, 0x92, 0xb8, 0x8b, 0x72, 0x40, 0x4f, 0x9d, 0xa1, 0x35, 0x69,
        0x86, 0x79, 0x26, 0x80, 0x41, 0xc5, 0x4a, 0x01, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff,
        0x02, 0x20, 0x4e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x22, 0x51, 0x20, 0x3b, 0x41, 0xda, 0xba,
        0x4c, 0x9a, 0xce, 0x57, 0x83, 0x69, 0x74, 0x0f, 0x15, 0xe5, 0xec, 0x88, 0x0c, 0x28, 0x27, 0x9e,
        0xe7, 0xf5, 0x1b, 0x07, 0xdc, 0xa6, 0x9c, 0x70, 0x61, 0xe0, 0x70, 0x68, 0xf8, 0x24, 0x01, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x16, 0x00, 0x14, 0x77, 0x52, 0xc1, 0x65, 0xea, 0x7b, 0xe7, 0x72, 0xb2,
        0xc0, 0xac, 0xb7, 0xf4, 0xd6, 0x04, 0x7a, 0xe6, 0xf4, 0x76, 0x8e, 0x01, 0x41, 0xcf, 0x5e, 0xfe,
        0x2d, 0x8e, 0xf1, 0x3e, 0xd0, 0xaf, 0x21, 0xd4, 0xf4, 0xcb, 0x82, 0x42, 0x2d, 0x62, 0x52, 0xd7,
        0x03, 0x24, 0xf6, 0xf4, 0x57, 0x6b, 0x72, 0x7b, 0x7d, 0x91, 0x8e, 0x52, 0x1c, 0x00, 0xb5, 0x1b,
        0xe7, 0x39, 0xdf, 0x2f, 0x89, 0x9c, 0x49, 0xdc, 0x26, 0x7c, 0x0a, 0xd2, 0x80, 0xac, 0xa6, 0xda,
        0xb0, 0xd2, 0xfa, 0x2b, 0x42, 0xa4, 0x51, 0x82, 0xfc, 0x83, 0xe8, 0x17, 0x13, 0x01, 0x00, 0x00,
        0x00, 0x00,
    ])
    tx = btc.core.Transaction.serialize_read(data)
    assert tx.serialize() == data
    assert tx.version == 1
    assert len(tx.vin) == 1
    assert len(tx.vout) == 2
    assert tx.locktime == 0
