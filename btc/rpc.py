import btc
import random
import requests
import typing

# Doc: https://developer.bitcoin.org/reference/rpc/


def call(method: str, params: typing.List[typing.Any]) -> typing.Any:
    r = requests.post(btc.config.current.rpc.addr, json={
        'id': random.randint(0x00000000, 0xffffffff),
        'jsonrpc': '2.0',
        'method': method,
        'params': params,
    }, auth=(
        btc.config.current.rpc.username,
        btc.config.current.rpc.password,
    )).json()
    if 'error' in r and r['error']:
        raise Exception(r['error'])
    return r['result']


def decode_raw_transaction(tx: str) -> typing.Dict:
    return call('decoderawtransaction', [tx])


def generate_to_address(nblocks: int, address: str) -> typing.List[str]:
    return call('generatetoaddress', [nblocks, address])


def get_best_block_hash() -> str:
    return call('getbestblockhash', [])


def get_block_count() -> int:
    return call('getblockcount', [])


def list_unspent(addresses: typing.List[str]) -> typing.List:
    return call('listunspent', [1, 9999999, addresses])
