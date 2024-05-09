import btc
import decimal
import itertools
import random
import requests
import time
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
    )).json(parse_float=decimal.Decimal)
    if 'error' in r and r['error']:
        raise Exception(r['error'])
    return r['result']


def decode_raw_transaction(tx: str) -> typing.Dict:
    return call('decoderawtransaction', [tx])


def estimates_mart_fee(conf_target: int) -> typing.Dict:
    # A mock is required on RegTest to allow this RPC to return meaningful data.
    # See: https://github.com/bitcoin/bitcoin/issues/11500
    if btc.config.current == btc.config.develop:
        return {'feerate': decimal.Decimal('0.00001'), 'blocks': conf_target}
    return call('estimatesmartfee', [conf_target])


def generate_to_address(nblocks: int, address: str) -> typing.List[str]:
    return call('generatetoaddress', [nblocks, address])


def get_best_block_hash() -> str:
    return call('getbestblockhash', [])


def get_block_count() -> int:
    return call('getblockcount', [])


def get_descriptor_info(descriptor: str) -> typing.Dict:
    return call('getdescriptorinfo', [descriptor])


def get_raw_transaction(txid: str, verbose: bool = False) -> typing.Dict:
    return call('getrawtransaction', [txid, verbose])


def get_tx_out(txid: str, vout: int) -> typing.Dict:
    return call('gettxout', [txid, vout])


def import_descriptors(requests: typing.List[typing.Dict]) -> typing.List[typing.Dict]:
    return call('importdescriptors', [requests])


def list_unspent(addresses: typing.List[str]) -> typing.List:
    return call('listunspent', [0, 9999999, addresses])


def send_raw_transaction(tx: str) -> str:
    return call('sendrawtransaction', [tx])


def wait(txid: str):
    if btc.config.current == btc.config.develop:
        return
    for _ in itertools.repeat(0):
        r = get_raw_transaction(txid, True)
        if r['in_active_chain']:
            break
        time.sleep(1)
