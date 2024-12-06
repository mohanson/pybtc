import argparse
import yabtc

# Calculate the address from a private key.

parser = argparse.ArgumentParser()
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--prikey', type=str, help='private key')
args = parser.parse_args()

if args.net == 'develop':
    yabtc.config.current = yabtc.config.develop
if args.net == 'mainnet':
    yabtc.config.current = yabtc.config.mainnet
if args.net == 'testnet':
    yabtc.config.current = yabtc.config.testnet

prikey = yabtc.core.PriKey(int(args.prikey, 0))
pubkey = prikey.pubkey()

print('p2pkh      ', yabtc.core.address_p2pkh(pubkey))
print('p2sh-p2wpkh', yabtc.core.address_p2sh_p2wpkh(pubkey))
print('p2wpkh     ', yabtc.core.address_p2wpkh(pubkey))
print('p2tr       ', yabtc.core.address_p2tr(pubkey, bytearray()))
