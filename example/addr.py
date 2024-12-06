import argparse
import pabtc

# Calculate the address from a private key.

parser = argparse.ArgumentParser()
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--prikey', type=str, help='private key')
args = parser.parse_args()

if args.net == 'develop':
    pabtc.config.current = pabtc.config.develop
if args.net == 'mainnet':
    pabtc.config.current = pabtc.config.mainnet
if args.net == 'testnet':
    pabtc.config.current = pabtc.config.testnet

prikey = pabtc.core.PriKey(int(args.prikey, 0))
pubkey = prikey.pubkey()

print('p2pkh      ', pabtc.core.address_p2pkh(pubkey))
print('p2sh-p2wpkh', pabtc.core.address_p2sh_p2wpkh(pubkey))
print('p2wpkh     ', pabtc.core.address_p2wpkh(pubkey))
print('p2tr       ', pabtc.core.address_p2tr(pubkey, bytearray()))
