import argparse
import btc

# Calculate the address from a private key.

parser = argparse.ArgumentParser()
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--prikey', type=str, help='private key')
args = parser.parse_args()

if args.net == 'develop':
    btc.config.current = btc.config.develop
if args.net == 'mainnet':
    btc.config.current = btc.config.mainnet
if args.net == 'testnet':
    btc.config.current = btc.config.testnet

prikey = btc.core.PriKey(int(args.prikey, 0))
pubkey = prikey.pubkey()

print('p2pkh      ', btc.core.address_p2pkh(pubkey))
print('p2sh-p2wpkh', btc.core.address_p2sh_p2wpkh(pubkey))
print('p2wpkh     ', btc.core.address_p2wpkh(pubkey))
print('p2tr       ', btc.core.address_p2tr(pubkey, bytearray()))
