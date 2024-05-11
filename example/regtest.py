import btc

btc.rpc.call('createwallet', ['main', True, True])
for d in [
    f'pkh({btc.core.PriKey(1).pubkey().sec().hex()})',
    f'pkh({btc.core.PriKey(2).pubkey().sec().hex()})',
    f'sh(wpkh({btc.core.PriKey(1).pubkey().sec().hex()}))',
    f'sh(wpkh({btc.core.PriKey(2).pubkey().sec().hex()}))',
    f'wpkh({btc.core.PriKey(1).pubkey().sec().hex()})',
    f'wpkh({btc.core.PriKey(2).pubkey().sec().hex()})',
    f'tr({btc.core.PriKey(1).pubkey().sec().hex()})',
    f'tr({btc.core.PriKey(2).pubkey().sec().hex()})',
]:
    d = btc.rpc.get_descriptor_info(d)['descriptor']
    btc.rpc.import_descriptors([{
        'desc': d,
        'timestamp': 0,
    }])
btc.rpc.generate_to_address(10, btc.core.address_p2pkh(btc.core.PriKey(1).pubkey()))
btc.rpc.generate_to_address(10, btc.core.address_p2sh_p2wpkh(btc.core.PriKey(1).pubkey()))
btc.rpc.generate_to_address(10, btc.core.address_p2wpkh(btc.core.PriKey(1).pubkey()))
btc.rpc.generate_to_address(10, btc.core.address_p2tr(btc.core.PriKey(1).pubkey()))
btc.rpc.generate_to_address(99, btc.core.address_p2pkh(btc.core.PriKey(1).pubkey()))
