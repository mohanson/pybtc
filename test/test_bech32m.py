import btc
import pytest


def test_bech32m():
    # Test vectors for Bech32m. See: https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki
    for s in [
        'A1LQFN3A',
        'a1lqfn3a',
        'an83characterlonghumanreadablepartthatcontainsthetheexcludedcharactersbioandnumber11sg7hg6',
        'abcdef1l7aum6echk45nj3s0wdvt2fg8x9yrzpqzd3ryx',
        '11llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllludsr8',
        'split1checkupstagehandshakeupstreamerranterredcaperredlc445v',
        '?1v759aa',
    ]:
        btc.bech32m.bech32m_decode(s)
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
            btc.bech32m.bech32m_decode(s)
