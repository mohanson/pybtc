import argparse
import yabtc

# Sign a message with the private key and verify it.

parser = argparse.ArgumentParser()
parser.add_argument('--msg', type=str, help='the message to create a signature of')
parser.add_argument('--prikey', type=str, help='private key')
parser.add_argument('--sig', type=str, default='', help='the signature of the message encoded in base 64')
args = parser.parse_args()

prikey = yabtc.core.PriKey(int(args.prikey, 0))
pubkey = prikey.pubkey()

if args.sig == '':
    print(yabtc.core.Message(args.msg).sign(prikey))

if args.sig != '':
    print(yabtc.core.Message(args.msg).pubkey(args.sig) == pubkey)
