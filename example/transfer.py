import argparse
import plbtc

# Transfer bitcoin to another account.

parser = argparse.ArgumentParser()
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--prikey', type=str, help='private key')
parser.add_argument('--script-type', type=str, choices=['p2pkh', 'p2sh-p2wpkh', 'p2wpkh', 'p2tr'])
parser.add_argument('--to', type=str, help='bitcoin address')
parser.add_argument('--value', type=float, help='bitcoin value')
args = parser.parse_args()

if args.net == 'develop':
    plbtc.config.current = plbtc.config.develop
if args.net == 'mainnet':
    plbtc.config.current = plbtc.config.mainnet
if args.net == 'testnet':
    plbtc.config.current = plbtc.config.testnet

accept_script = plbtc.core.script_pubkey(args.to)
accept_value = int(args.value * plbtc.denomination.bitcoin)
prikey = int(args.prikey, 0)
if args.script_type == 'p2pkh':
    wallet = plbtc.wallet.Wallet(plbtc.wallet.Tp2pkh(prikey))
if args.script_type == 'p2sh-p2wpkh':
    wallet = plbtc.wallet.Wallet(plbtc.wallet.Tp2shp2wpkh(prikey))
if args.script_type == 'p2wpkh':
    wallet = plbtc.wallet.Wallet(plbtc.wallet.Tp2wpkh(prikey))
if args.script_type == 'p2tr':
    wallet = plbtc.wallet.Wallet(plbtc.wallet.Tp2tr(prikey, bytearray()))
txid = wallet.transfer(accept_script, accept_value)
print(f'0x{txid.hex()}')
