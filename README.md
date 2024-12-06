# Yabtc: Bitcoin Library For Humans

Yabtc is a project that aims to provide human-friendly interfaces for common btc operations. Using yabtc, you can easily and happily complete everything you want to do on btc.

Features:

- No third-party dependencies, everything is visible.
- Incredibly simple, even a cat knows how to use it.

## Installation

```sh
$ pip install yabtc
# or
$ git clone https://github.com/mohanson/yabtc
$ cd yabtc
$ python -m pip install --editable .
```

## Usage

By default, yabtc is configured on the develop. To switch networks, use `yabtc.config.current = yabtc.config.mainnet`.

**example/addr.py**

Calculate the address from a private key.

```sh
$ python example/addr.py --net mainnet --prikey 1

# p2pkh       1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH
# p2sh-p2wpkh 3JvL6Ymt8MVWiCNHC7oWU6nLeHNJKLZGLN
# p2wpkh      bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4
# p2tr        bc1pmfr3p9j00pfxjh0zmgp99y8zftmd3s5pmedqhyptwy6lm87hf5sspknck9
```

**example/message.py**

Sign a message with the private key and verify it.

```sh
$ python example/message.py --prikey 1 --msg pybtc
# ICvzXjwjJVMilSGyMqwlqMTuGF6UMwddFJzVmm0Di5qNnqkBRKP8Pldm3YbOskg3ewV1tszVLy8gVX1u+qFrx6o=

$ python example/message.py --prikey 1 --msg pybtc --sig ICvzXjwjJVMilSGyMqwlqMTuGF6UMwddFJzVmm0Di5qNnqkBRKP8Pldm3YbOskg3ewV1tszVLy8gVX1u+qFrx6o=
# True
```


**example/taproot.py**

This example demonstrates how to create a P2TR script with two script spending paths: p2pk and p2ms(2-of-2 multisig).

```sh
$ python example/taproot.py
```

**example/transfer.py**

Transfer Bitcoin to another account. Pybtc supports four common types of Bitcoin transactions: P2PKH, P2SH-P2WPKH, P2WPKH, and P2TR. For more complex account types, such as P2SH-P2MS, please refer to [test/test_wallet.py](test/test_wallet.py).

```sh
$ python example/transfer.py --net develop --prikey 1 --script-type p2pkh --to mg8Jz5776UdyiYcBb9Z873NTozEiADRW5H --value 0.1

# 0x039d1b0fe969d33341a7db9ddd236f632d6851292200603abc5a6c7738bf3079
```

Before using this script, you first need to execute the code in the Test section. This is because pybtc requires the bitcoin core wallet to provide an account's utxo set.

## Test

The testing of this project relies on regtest. You can set up the regtest node using the following steps:

```sh
$ wget https://bitcoincore.org/bin/bitcoin-core-27.1/bitcoin-27.1-x86_64-linux-gnu.tar.gz
$ tar -xvf bitcoin-27.1-x86_64-linux-gnu.tar.gz
$ cp -R bitcoin-27.1 ~/app/bitcoin # Install to the target location.

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
