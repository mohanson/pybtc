import btc
import itertools


def test_wallet_transfer():
    btc.config.current = btc.config.develop
    script_type_list = [
        btc.core.script_type_p2pkh,
        btc.core.script_type_p2sh,
        btc.core.script_type_p2wpkh,
    ]
    for user_type, mate_type in itertools.product(script_type_list, script_type_list):
        user = btc.wallet.Wallet(1, user_type)
        mate = btc.wallet.Wallet(2, mate_type)
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
