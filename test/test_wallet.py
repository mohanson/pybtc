import btc
import itertools


def test_wallet_transfer():
    btc.config.current = btc.config.develop
    user_list = [
        btc.wallet.Wallet(btc.wallet.Tp2pkh(1)),
        btc.wallet.Wallet(btc.wallet.Tp2shp2wpkh(1)),
        btc.wallet.Wallet(btc.wallet.Tp2wpkh(1)),
        btc.wallet.Wallet(btc.wallet.Tp2tr(1)),
    ]
    mate_list = [
        btc.wallet.Wallet(btc.wallet.Tp2pkh(2)),
        btc.wallet.Wallet(btc.wallet.Tp2shp2wpkh(2)),
        btc.wallet.Wallet(btc.wallet.Tp2wpkh(2)),
        btc.wallet.Wallet(btc.wallet.Tp2tr(2)),
    ]
    for user, mate in itertools.product(user_list, mate_list):
        value = btc.denomination.bitcoin
        value_old = mate.balance()
        txid = user.transfer(mate.script, value)
        btc.rpc.wait(txid[::-1].hex())
        value_new = mate.balance()
        assert value_new - value_old == value
        value_old = value_new
        txid = user.transfer(mate.script, value)
        btc.rpc.wait(txid[::-1].hex())
        value_new = mate.balance()
        assert value_new - value_old == value
        btc.rpc.generate_to_address(6, user.addr)
        txid = mate.transfer_all(user.script)
        btc.rpc.wait(txid[::-1].hex())
        assert mate.balance() == 0
