import argparse
import btc

# Transfer bitcoin to another account.

parser = argparse.ArgumentParser()
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--prikey', type=str, help='private key')
parser.add_argument('--script-type', type=str, choices=['p2pkh', 'p2sh', 'p2wpkh', 'p2tr'])
parser.add_argument('--to', type=str, help='bitcoin address')
parser.add_argument('--value', type=float, help='bitcoin value')
args = parser.parse_args()

if args.net == 'develop':
    btc.config.current = btc.config.develop
if args.net == 'mainnet':
    btc.config.current = btc.config.mainnet
if args.net == 'testnet':
    btc.config.current = btc.config.testnet

if args.script_type == 'p2pkh':
    script_type = btc.core.script_type_p2pkh
if args.script_type == 'p2sh':
    script_type = btc.core.script_type_p2sh
if args.script_type == 'p2wpkh':
    script_type = btc.core.script_type_p2wpkh
if args.script_type == 'p2tr':
    script_type = btc.core.script_type_p2tr

accept_script = btc.core.script_pubkey(args.to)
accept_value = int(args.value * btc.denomination.bitcoin)
prikey = int(args.prikey, 0)
wallet = btc.wallet.Wallet(prikey, script_type)
txid = wallet.transfer(accept_script, accept_value)
print(f'0x{txid.hex()}')
