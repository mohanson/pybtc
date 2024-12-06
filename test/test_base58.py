import random
import pabtc


def test_base58_encode():
    assert pabtc.base58.encode(bytearray.fromhex('00')) == '1'
    assert pabtc.base58.encode(bytearray.fromhex('626262')) == 'a3gV'
    assert pabtc.base58.encode(bytearray.fromhex('636363')) == 'aPEr'


def test_base58_decode():
    assert pabtc.base58.decode('1') == bytearray.fromhex('00')
    assert pabtc.base58.decode('a3gV') == bytearray.fromhex('626262')
    assert pabtc.base58.decode('aPEr') == bytearray.fromhex('636363')


def test_base58_random():
    for _ in range(256):
        b = bytearray(random.randbytes(random.randint(0, 256)))
        s = pabtc.base58.encode(b)
        f = pabtc.base58.decode(s)
        assert b == f
