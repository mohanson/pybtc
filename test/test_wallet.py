import btc


def test_wallet_transfer():
    btc.config.current = btc.config.develop
    user = btc.wallet.Wallet(1, btc.core.script_type_p2pkh)
    mate = btc.wallet.Wallet(2, btc.core.script_type_p2pkh)
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


def test_wallet_p2wpkh_transfer():
    btc.config.current = btc.config.develop
    user = btc.wallet.WalletSegwit(1)
    mate = btc.wallet.WalletSegwit(2)
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
