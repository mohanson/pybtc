import argparse
import btc

# Calculate the address from a private key.

parser = argparse.ArgumentParser()
parser.add_argument('prikey', type=str, help='private key')
args = parser.parse_args()

base = 10
if args.prikey.startswith('0x'):
    base = 16

prikey = btc.core.PriKey(int(args.prikey, base))
pubkey = prikey.pubkey()

print('p2pkh ', btc.core.address_p2pkh(pubkey))
print('p2sh  ', btc.core.address_p2sh(pubkey))
print('p2wpkh', btc.core.address_p2wpkh(pubkey))
print('p2tr  ', btc.core.address_p2tr(pubkey))
