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

## Test

The testing of this project depends on regtest. You can use the following steps to build the regtest node.

```sh
$ wget https://bitcoincore.org/bin/bitcoin-core-27.0/bitcoin-27.0-x86_64-linux-gnu.tar.gz
$ tar -zxvf bitcoin-27.0-x86_64-linux-gnu.tar.gz
$ cp -R bitcoin-27.0 ~/app/bitcoin # Install to the target location.

$ mkdir ~/.bitcoin
$ echo "chain=regtest" >> ~/.bitcoin/bitcoin.conf
$ echo "deprecatedrpc=create_bdb" >> ~/.bitcoin/bitcoin.conf
$ echo "rpcpassword=pass" >> ~/.bitcoin/bitcoin.conf
$ echo "rpcuser=user" >> ~/.bitcoin/bitcoin.conf
$ echo "txindex=1" >> ~/.bitcoin/bitcoin.conf

$ bitcoind
$ bitcoin-cli -named createwallet wallet_name=main descriptors=false load_on_startup=true
$ bitcoin-cli importaddress mrCDrCybB6J1vRfbwM5hemdJz73FwDBC8r
$ bitcoin-cli importaddress mg8Jz5776UdyiYcBb9Z873NTozEiADRW5H
$ bitcoin-cli importaddress bcrt1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080
$ bitcoin-cli importaddress bcrt1qq6hag67dl53wl99vzg42z8eyzfz2xlkvwk6f7m

$ bitcoin-cli generatetoaddress 101 mrCDrCybB6J1vRfbwM5hemdJz73FwDBC8r
$ bitcoin-cli generatetoaddress 101 bcrt1qw508d6qejxtdg4y5r3zarvary0c5xw7kygt080

$ pytest -v
```

## License

MIT
