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
$ python example/addr.py --net mainnet --prikey 1

# p2pkh       1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH
# p2sh-p2wpkh 3JvL6Ymt8MVWiCNHC7oWU6nLeHNJKLZGLN
# p2wpkh      bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4
# p2tr        bc1pmfr3p9j00pfxjh0zmgp99y8zftmd3s5pmedqhyptwy6lm87hf5sspknck9
```

**example/transfer.py**

Transfer bitcoin to another account. Pybtc has implemented a bitcoin core utxo searcher by default, you can refer to the Test chapter to configure the bitcoin core regtest node. Supports all four types of Bitcoin transactions: P2PKH, P2SH-P2WPKH, P2WPKH and P2TR.

```sh
$ python example/transfer.py --net develop --prikey 1 --script-type p2pkh --to mg8Jz5776UdyiYcBb9Z873NTozEiADRW5H --value 0.1

# 0x039d1b0fe969d33341a7db9ddd236f632d6851292200603abc5a6c7738bf3079
```

You can implement the utxo searcher yourself so you don't have to rely on the bitcoin core wallet. Reference: [btc.wallet.Searcher](btc/wallet.py)

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
# Create default wallets
$ python example/regtest.py
$ pytest -v
```

## License

MIT
