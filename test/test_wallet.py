import itertools
import yabtc


def test_wallet_transfer():
    yabtc.config.current = yabtc.config.develop
    user_list = [
        yabtc.wallet.Wallet(yabtc.wallet.Tp2pkh(1)),
        yabtc.wallet.Wallet(yabtc.wallet.Tp2shp2ms([yabtc.core.PriKey(e).pubkey() for e in [1, 2]], [1, 2])),
        yabtc.wallet.Wallet(yabtc.wallet.Tp2shp2wpkh(1)),
        yabtc.wallet.Wallet(yabtc.wallet.Tp2wpkh(1)),
        yabtc.wallet.Wallet(yabtc.wallet.Tp2tr(1, bytearray())),
    ]
    mate_list = [
        yabtc.wallet.Wallet(yabtc.wallet.Tp2pkh(2)),
        yabtc.wallet.Wallet(yabtc.wallet.Tp2shp2ms([yabtc.core.PriKey(e).pubkey() for e in [2, 1]], [2, 1])),
        yabtc.wallet.Wallet(yabtc.wallet.Tp2shp2wpkh(2)),
        yabtc.wallet.Wallet(yabtc.wallet.Tp2wpkh(2)),
        yabtc.wallet.Wallet(yabtc.wallet.Tp2tr(2, bytearray())),
    ]
    for user, mate in itertools.product(user_list, mate_list):
        value = yabtc.denomination.bitcoin
        value_old = mate.balance()
        txid = user.transfer(mate.script, value)
        yabtc.rpc.wait(txid[::-1].hex())
        value_new = mate.balance()
        assert value_new - value_old == value
        value_old = value_new
        txid = user.transfer(mate.script, value)
        yabtc.rpc.wait(txid[::-1].hex())
        value_new = mate.balance()
        assert value_new - value_old == value
        yabtc.rpc.generate_to_address(6, user.addr)
        txid = mate.transfer_all(user.script)
        yabtc.rpc.wait(txid[::-1].hex())
        assert mate.balance() == 0
