import argparse
import plbtc

# Calculate the address from a private key.

parser = argparse.ArgumentParser()
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--prikey', type=str, help='private key')
args = parser.parse_args()

if args.net == 'develop':
    plbtc.config.current = plbtc.config.develop
if args.net == 'mainnet':
    plbtc.config.current = plbtc.config.mainnet
if args.net == 'testnet':
    plbtc.config.current = plbtc.config.testnet

prikey = plbtc.core.PriKey(int(args.prikey, 0))
pubkey = prikey.pubkey()

print('p2pkh      ', plbtc.core.address_p2pkh(pubkey))
print('p2sh-p2wpkh', plbtc.core.address_p2sh_p2wpkh(pubkey))
print('p2wpkh     ', plbtc.core.address_p2wpkh(pubkey))
print('p2tr       ', plbtc.core.address_p2tr(pubkey, bytearray()))
