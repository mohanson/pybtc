import random
import yabtc


def test_base58_encode():
    assert yabtc.base58.encode(bytearray.fromhex('00')) == '1'
    assert yabtc.base58.encode(bytearray.fromhex('626262')) == 'a3gV'
    assert yabtc.base58.encode(bytearray.fromhex('636363')) == 'aPEr'


def test_base58_decode():
    assert yabtc.base58.decode('1') == bytearray.fromhex('00')
    assert yabtc.base58.decode('a3gV') == bytearray.fromhex('626262')
    assert yabtc.base58.decode('aPEr') == bytearray.fromhex('636363')


def test_base58_random():
    for _ in range(256):
        b = bytearray(random.randbytes(random.randint(0, 256)))
        s = yabtc.base58.encode(b)
        f = yabtc.base58.decode(s)
        assert b == f
