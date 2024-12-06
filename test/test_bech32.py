import pytest
import yabtc


def test_bech32():
    # See: https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki
    for s in [
        'A12UEL5L',
        'a12uel5l',
        'an83characterlonghumanreadablepartthatcontainsthenumber1andtheexcludedcharactersbio1tt5tgs',
        'abcdef1qpzry9x8gf2tvdw0s3jn54khce6mua7lmqqqxw',
        '11qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqc8247j',
        'split1checkupstagehandshakeupstreamerranterredcaperred2y9e3w',
        '?1ezyfcl',
    ]:
        hrp, data = yabtc.bech32.bech32_decode(0, s)
        assert yabtc.bech32.bech32_encode(hrp, 0, data) == s.lower()
    for s in [
        '\x20' + '1nwldj5',
        '\x7F' + '1axkwrx',
        '\x80' + '1eym55h',
        'an84characterslonghumanreadablepartthatcontainsthenumber1andtheexcludedcharactersbio1569pvx',
        'pzry9x0s0muk',
        '1pzry9x0s0muk',
        'x1b4n0q5v',
        'li1dgmt3',
        'de1lg7wt',
        'A1G7SGD8',
        '10a06t8',
        '1qzzfhee',
    ]:
        with pytest.raises(AssertionError):
            yabtc.bech32.bech32_decode(0, s)


def test_bech32m():
    # See: https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki
    for s in [
        'A1LQFN3A',
        'a1lqfn3a',
        'an83characterlonghumanreadablepartthatcontainsthetheexcludedcharactersbioandnumber11sg7hg6',
        'abcdef1l7aum6echk45nj3s0wdvt2fg8x9yrzpqzd3ryx',
        '11llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllludsr8',
        'split1checkupstagehandshakeupstreamerranterredcaperredlc445v',
        '?1v759aa',
    ]:
        hrp, data = yabtc.bech32.bech32_decode(1, s)
        assert yabtc.bech32.bech32_encode(hrp, 1, data) == s.lower()
    for s in [
        '\x20' + '1xj0phk',
        '\x7F' + '1g6xzxy',
        '\x80' + '1vctc34',
        'an84characterslonghumanreadablepartthatcontainsthetheexcludedcharactersbioandnumber11d6pts4',
        'qyrz8wqd2c9m',
        '1qyrz8wqd2c9m',
        'y1b0jsk6g',
        'lt1igcx5c0',
        'in1muywd',
        'mm1crxm3i',
        'au1s5cgom',
        'M1VUXWEZ',
        '16plkw9',
        '1p2gdwpf',
    ]:
        with pytest.raises(AssertionError):
            yabtc.bech32.bech32_decode(1, s)
