import itertools
import plbtc


def test_wallet_transfer():
    plbtc.config.current = plbtc.config.develop
    user_list = [
        plbtc.wallet.Wallet(plbtc.wallet.Tp2pkh(1)),
        plbtc.wallet.Wallet(plbtc.wallet.Tp2shp2ms([plbtc.core.PriKey(e).pubkey() for e in [1, 2]], [1, 2])),
        plbtc.wallet.Wallet(plbtc.wallet.Tp2shp2wpkh(1)),
        plbtc.wallet.Wallet(plbtc.wallet.Tp2wpkh(1)),
        plbtc.wallet.Wallet(plbtc.wallet.Tp2tr(1, bytearray())),
    ]
    mate_list = [
        plbtc.wallet.Wallet(plbtc.wallet.Tp2pkh(2)),
        plbtc.wallet.Wallet(plbtc.wallet.Tp2shp2ms([plbtc.core.PriKey(e).pubkey() for e in [2, 1]], [2, 1])),
        plbtc.wallet.Wallet(plbtc.wallet.Tp2shp2wpkh(2)),
        plbtc.wallet.Wallet(plbtc.wallet.Tp2wpkh(2)),
        plbtc.wallet.Wallet(plbtc.wallet.Tp2tr(2, bytearray())),
    ]
    for user, mate in itertools.product(user_list, mate_list):
        value = plbtc.denomination.bitcoin
        value_old = mate.balance()
        txid = user.transfer(mate.script, value)
        plbtc.rpc.wait(txid[::-1].hex())
        value_new = mate.balance()
        assert value_new - value_old == value
        value_old = value_new
        txid = user.transfer(mate.script, value)
        plbtc.rpc.wait(txid[::-1].hex())
        value_new = mate.balance()
        assert value_new - value_old == value
        plbtc.rpc.generate_to_address(6, user.addr)
        txid = mate.transfer_all(user.script)
        plbtc.rpc.wait(txid[::-1].hex())
        assert mate.balance() == 0
