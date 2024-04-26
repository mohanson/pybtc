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

**example/addrr.py**

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
$ echo "rpcpassword=pass" >> ~/.bitcoin/bitcoin.conf
$ echo "rpcuser=user" >> ~/.bitcoin/bitcoin.conf

$ bitcoind
```

## License

MIT
