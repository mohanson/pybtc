import btc
import itertools


def test_wallet_transfer():
    btc.config.current = btc.config.develop
    user_list = [
        btc.wallet.Wallet(1, btc.core.script_type_p2pkh),
        btc.wallet.Wallet(1, btc.core.script_type_p2sh_p2wpkh),
        btc.wallet.Wallet(1, btc.core.script_type_p2wpkh),
        btc.wallet.Wallet(1, btc.core.script_type_p2tr),
    ]
    mate_list = [
        btc.wallet.Wallet(2, btc.core.script_type_p2pkh),
        btc.wallet.Wallet(2, btc.core.script_type_p2sh_p2wpkh),
        btc.wallet.Wallet(2, btc.core.script_type_p2wpkh),
        btc.wallet.Wallet(2, btc.core.script_type_p2tr),
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
