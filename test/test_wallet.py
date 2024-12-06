import itertools
import pabtc


def test_wallet_transfer():
    pabtc.config.current = pabtc.config.develop
    user_list = [
        pabtc.wallet.Wallet(pabtc.wallet.Tp2pkh(1)),
        pabtc.wallet.Wallet(pabtc.wallet.Tp2shp2ms([pabtc.core.PriKey(e).pubkey() for e in [1, 2]], [1, 2])),
        pabtc.wallet.Wallet(pabtc.wallet.Tp2shp2wpkh(1)),
        pabtc.wallet.Wallet(pabtc.wallet.Tp2wpkh(1)),
        pabtc.wallet.Wallet(pabtc.wallet.Tp2tr(1, bytearray())),
    ]
    mate_list = [
        pabtc.wallet.Wallet(pabtc.wallet.Tp2pkh(2)),
        pabtc.wallet.Wallet(pabtc.wallet.Tp2shp2ms([pabtc.core.PriKey(e).pubkey() for e in [2, 1]], [2, 1])),
        pabtc.wallet.Wallet(pabtc.wallet.Tp2shp2wpkh(2)),
        pabtc.wallet.Wallet(pabtc.wallet.Tp2wpkh(2)),
        pabtc.wallet.Wallet(pabtc.wallet.Tp2tr(2, bytearray())),
    ]
    for user, mate in itertools.product(user_list, mate_list):
        value = pabtc.denomination.bitcoin
        value_old = mate.balance()
        txid = user.transfer(mate.script, value)
        pabtc.rpc.wait(txid[::-1].hex())
        value_new = mate.balance()
        assert value_new - value_old == value
        value_old = value_new
        txid = user.transfer(mate.script, value)
        pabtc.rpc.wait(txid[::-1].hex())
        value_new = mate.balance()
        assert value_new - value_old == value
        pabtc.rpc.generate_to_address(6, user.addr)
        txid = mate.transfer_all(user.script)
        pabtc.rpc.wait(txid[::-1].hex())
        assert mate.balance() == 0
