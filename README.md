# Python SDK for BTC

Python BTC is an experimental project that aims to provide human-friendly interfaces for common BTC operations. Note that Python BTC is not a complete SDK, but only implements the BTC functions that I am interested in.

Features:

- No third-party dependencies. All code is visible.
- Incredibly simple.

## Installation

```sh
$ git clone https://github.com/mohanson/pybtc
$ cd pybtc
$ python -m pip install --editable . --config-settings editable_mode=strict
```

## Usage

**example/addr.py**

Calculate the address from a private key.

```sh
$ python example/addr.py --net mainnet --prikey 0x0000000000000000000000000000000000000000000000000000000000000001

# p2pkh  1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH
# p2sh   3JvL6Ymt8MVWiCNHC7oWU6nLeHNJKLZGLN
# p2wpkh bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4
# p2tr   bc1pmfr3p9j00pfxjh0zmgp99y8zftmd3s5pmedqhyptwy6lm87hf5sspknck9
```

**example/transfer.py**

Transfer bitcoin to another account. Pybtc has implemented a bitcoin core utxo searcher by default, you can refer to the Test chapter to configure the bitcoin core regtest node.

```sh
$ python example/transfer.py --net develop --prikey 1 --script-type p2pkh --to mg8Jz5776UdyiYcBb9Z873NTozEiADRW5H --value 0.1

# 0x039d1b0fe969d33341a7db9ddd236f632d6851292200603abc5a6c7738bf3079
```

You can implement the utxo searcher yourself so you don't have to rely on the bitcoin core wallet. Reference: [btc.wallet.WalletUtxoSearchFromBitcoinCore](btc/wallet.py)

## Test

The testing of this project depends on regtest. You can use the following steps to build the regtest node.

```sh
$ wget https://bitcoincore.org/bin/bitcoin-core-27.0/bitcoin-27.0-x86_64-linux-gnu.tar.gz
$ tar -zxvf bitcoin-27.0-x86_64-linux-gnu.tar.gz
$ cp -R bitcoin-27.0 ~/app/bitcoin # Install to the target location.

$ mkdir ~/.bitcoin
$ echo "chain=regtest" >> ~/.bitcoin/bitcoin.conf
$ echo "rpcpassword=pass" >> ~/.bitcoin/bitcoin.conf
$ echo "rpcuser=user" >> ~/.bitcoin/bitcoin.conf
$ echo "txindex=1" >> ~/.bitcoin/bitcoin.conf

$ bitcoind
$ bitcoin-cli -named createwallet wallet_name=main disable_private_keys=true load_on_startup=true

$ bitcoin-cli getdescriptorinfo 'pkh(0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798)'
$ bitcoin-cli getdescriptorinfo 'sh(wpkh(0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798))'
$ bitcoin-cli getdescriptorinfo 'wpkh(0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798)'
$ bitcoin-cli getdescriptorinfo 'tr(0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798)'
$ bitcoin-cli importdescriptors '[{ "desc": "pkh(0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798)#e48zzw02", "timestamp":0 }]'
$ bitcoin-cli importdescriptors '[{ "desc": "sh(wpkh(0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798))#jqtwwlah", "timestamp":0 }]'
$ bitcoin-cli importdescriptors '[{ "desc": "wpkh(0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798)#ucxz0gak", "timestamp":0 }]'
$ bitcoin-cli importdescriptors '[{ "desc": "tr(0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798)#3q50ef67", "timestamp":0 }]'
$ bitcoin-cli getdescriptorinfo 'pkh(02c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5)'
$ bitcoin-cli getdescriptorinfo 'sh(wpkh(02c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5))'
$ bitcoin-cli getdescriptorinfo 'wpkh(02c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5)'
$ bitcoin-cli getdescriptorinfo 'tr(02c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5)'
$ bitcoin-cli importdescriptors '[{ "desc": "pkh(02c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5)#8fhd9pwu", "timestamp":0 }]'
$ bitcoin-cli importdescriptors '[{ "desc": "sh(wpkh(02c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5))#la26f59y", "timestamp":0 }]'
$ bitcoin-cli importdescriptors '[{ "desc": "wpkh(02c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5)#wg9vgf99", "timestamp":0 }]'
$ bitcoin-cli importdescriptors '[{ "desc": "tr(02c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5)#g74uw3rl", "timestamp":0 }]'

$ bitcoin-cli generatetoaddress 10 mrCDrCybB6J1vRfbwM5hemdJz73FwDBC8r
$ bitcoin-cli generatetoaddress 10 2NAUYAHhujozruyzpsFRP63mbrdaU5wnEpN
$ bitcoin-cli generatetoaddress 10 bcrt1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080
$ bitcoin-cli generatetoaddress 10 bcrt1pmfr3p9j00pfxjh0zmgp99y8zftmd3s5pmedqhyptwy6lm87hf5ssm803es
$ bitcoin-cli generatetoaddress 99 mrCDrCybB6J1vRfbwM5hemdJz73FwDBC8r
$ pytest -v
```

## License

MIT
