import btc
import random
import requests
import typing


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


def get_block_count() -> int:
    return call('getblockcount', [])
