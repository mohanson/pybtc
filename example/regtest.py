import btc

pub1 = btc.core.PriKey(1).pubkey()
pub2 = btc.core.PriKey(2).pubkey()

btc.rpc.call('createwallet', ['main', True, True, None, None, None, True])
for d in [
    f'pkh({pub1.sec().hex()})',
    f'pkh({pub2.sec().hex()})',
    f'sh(multi(2,{pub1.sec().hex()},{pub2.sec().hex()}))',
    f'sh(multi(2,{pub2.sec().hex()},{pub1.sec().hex()}))',
    f'sh(wpkh({pub1.sec().hex()}))',
    f'sh(wpkh({pub2.sec().hex()}))',
    f'wpkh({pub1.sec().hex()})',
    f'wpkh({pub2.sec().hex()})',
    f'tr({pub1.sec().hex()})',
    f'tr({pub2.sec().hex()})',
]:
    d = btc.rpc.get_descriptor_info(d)['descriptor']
    btc.rpc.import_descriptors([{
        'desc': d,
        'timestamp': 0,
    }])
btc.rpc.generate_to_address(10, btc.core.address_p2pkh(pub1))
btc.rpc.generate_to_address(10, btc.core.address_p2sh_p2ms(2, [pub1, pub2]))
btc.rpc.generate_to_address(10, btc.core.address_p2sh_p2wpkh(pub1))
btc.rpc.generate_to_address(10, btc.core.address_p2wpkh(pub1))
btc.rpc.generate_to_address(10, btc.core.address_p2tr(pub1, bytearray()))
btc.rpc.generate_to_address(99, btc.core.address_p2pkh(pub1))
