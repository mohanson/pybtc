import random
import plbtc


def test_base58_encode():
    assert plbtc.base58.encode(bytearray.fromhex('00')) == '1'
    assert plbtc.base58.encode(bytearray.fromhex('626262')) == 'a3gV'
    assert plbtc.base58.encode(bytearray.fromhex('636363')) == 'aPEr'


def test_base58_decode():
    assert plbtc.base58.decode('1') == bytearray.fromhex('00')
    assert plbtc.base58.decode('a3gV') == bytearray.fromhex('626262')
    assert plbtc.base58.decode('aPEr') == bytearray.fromhex('636363')


def test_base58_random():
    for _ in range(256):
        b = bytearray(random.randbytes(random.randint(0, 256)))
        s = plbtc.base58.encode(b)
        f = plbtc.base58.decode(s)
        assert b == f
