import decimal
import itertools
import random
import requests
import time
import typing
import plbtc.config

# Doc: https://developer.bitcoin.org/reference/rpc/


def call(method: str, params: typing.List[typing.Any]) -> typing.Any:
    r = requests.post(plbtc.config.current.rpc.addr, json={
        'id': random.randint(0x00000000, 0xffffffff),
        'jsonrpc': '2.0',
        'method': method,
        'params': params,
    }, auth=(
        plbtc.config.current.rpc.username,
        plbtc.config.current.rpc.password,
    )).json(parse_float=decimal.Decimal)
    if 'error' in r and r['error']:
        raise Exception(r['error'])
    return r['result']


def wait(txid: str):
    if plbtc.config.current == plbtc.config.develop:
        return
    for _ in itertools.repeat(0):
        r = get_raw_transaction(txid)
        if r['in_active_chain']:
            break
        time.sleep(1)

# =============================================================================
# Blockchain RPCs
# =============================================================================


def get_best_block_hash() -> str:
    return call('getbestblockhash', [])


def get_block(blockhash: str) -> typing.Dict:
    return call('getblock', [blockhash])


def get_block_chain_info():
    pass


def get_block_count() -> int:
    return call('getblockcount', [])


def get_block_filter():
    pass


def get_block_hash():
    pass


def get_block_header(blockhash: str) -> typing.Dict:
    return call('getblockheader', [blockhash, True])


def get_block_stats():
    pass


def get_chain_tips():
    pass


def get_chain_tx_stats():
    pass


def get_difficulty() -> decimal.Decimal:
    return call('getdifficulty', [])


def get_mempool_ancestors():
    pass


def get_mempool_descendants():
    pass


def get_mempool_entry():
    pass


def get_mempool_info():
    pass


def get_raw_mempool():
    pass


def get_tx_out(txid: str, vout: int) -> typing.Dict:
    return call('gettxout', [txid, vout])


def get_tx_out_proof():
    pass


def get_tx_out_set_info():
    pass


def precious_block():
    pass


def prune_blockchain():
    pass


def save_mempool():
    pass


def scan_tx_out_set():
    pass


def verify_chain():
    pass


def verify_tx_out_proof():
    pass

# =============================================================================
# Control RPCs
# =============================================================================


def get_memory_info():
    pass


def get_rpc_info():
    pass


def help():
    pass


def logging():
    pass


def stop():
    pass


def uptime():
    pass

# =============================================================================
# Generating RPCs
# =============================================================================


def generate_block():
    pass


def generate_to_address(nblocks: int, address: str) -> typing.List[str]:
    return call('generatetoaddress', [nblocks, address])


def generate_to_descriptor(nblocks: int, descriptor: str) -> typing.List[str]:
    return call('generatetodescriptor', [nblocks, descriptor])

# =============================================================================
# Mining RPCs
# =============================================================================


def get_block_template():
    pass


def get_mining_info():
    pass


def get_network_hashps():
    pass


def prioritise_transaction():
    pass


def submit_block():
    pass


def submit_header():
    pass

# =============================================================================
# Network RPCs
# =============================================================================


def addnode():
    pass


def clear_banned():
    pass


def disconnect_node():
    pass


def get_added_node_info():
    pass


def get_connection_count():
    pass


def get_net_totals():
    pass


def get_network_info():
    pass


def get_node_addresses():
    pass


def get_peer_info():
    pass


def list_banned():
    pass


def ping():
    pass


def set_ban():
    pass


def set_network_active():
    pass

# =============================================================================
# Rawtransactions RPCs
# =============================================================================


def analyze_psbt():
    pass


def combine_psbt():
    pass


def combine_raw_transaction():
    pass


def convert_to_psbt():
    pass


def create_psbt():
    pass


def create_raw_transaction():
    pass


def decode_psbt():
    pass


def decode_raw_transaction(tx: str) -> typing.Dict:
    return call('decoderawtransaction', [tx])


def decode_script():
    pass


def finalize_psbt():
    pass


def fund_raw_transaction():
    pass


def get_raw_transaction(txid: str) -> typing.Dict:
    return call('getrawtransaction', [txid])


def join_psbts():
    pass


def send_raw_transaction(tx: str) -> str:
    return call('sendrawtransaction', [tx])


def sign_raw_transaction_with_key():
    pass


def test_mempool_accept():
    pass


def utxo_update_psbt():
    pass

# =============================================================================
# Util RPCs
# =============================================================================


def create_multisig():
    pass


def derive_addresses():
    pass


def estimates_mart_fee(conf_target: int) -> typing.Dict:
    # A mock is required on RegTest to allow this RPC to return meaningful data.
    # See: https://github.com/bitcoin/bitcoin/issues/11500
    if plbtc.config.current == plbtc.config.develop:
        return {'feerate': decimal.Decimal('0.00001'), 'blocks': conf_target}
    return call('estimatesmartfee', [conf_target, 'ECONOMICAL'])


def get_descriptor_info(descriptor: str) -> typing.Dict:
    return call('getdescriptorinfo', [descriptor])


def get_index_info():
    pass


def sign_message_with_privkey():
    pass


def validate_address():
    pass


def verify_message():
    pass

# =============================================================================
# Wallet RPCs
# =============================================================================


def abandon_transaction():
    pass


def abort_rescan():
    pass


def add_multisig_address():
    pass


def backup_wallet():
    pass


def bump_fee():
    pass


def create_wallet():
    pass


def dump_privkey():
    pass


def dump_wallet():
    pass


def encrypt_wallet():
    pass


def get_addresses_by_label():
    pass


def get_address_info():
    pass


def get_balance():
    pass


def get_balances():
    pass


def get_new_address():
    pass


def get_raw_change_address():
    pass


def get_received_by_address():
    pass


def get_received_by_label():
    pass


def get_transaction():
    pass


def get_unconfirmed_balance():
    pass


def get_wallet_info():
    pass


def import_address():
    pass


def import_descriptors(requests: typing.List[typing.Dict]) -> typing.List[typing.Dict]:
    return call('importdescriptors', [requests])


def import_multi():
    pass


def import_privkey():
    pass


def import_pruned_funds():
    pass


def import_pubkey():
    pass


def import_wallet():
    pass


def keypool_refill():
    pass


def list_address_groupings():
    pass


def list_labels():
    pass


def list_lock_unspent():
    pass


def list_received_by_address():
    pass


def list_received_by_label():
    pass


def list_since_block():
    pass


def list_transactions():
    pass


def list_unspent(addresses: typing.List[str]) -> typing.List:
    return call('listunspent', [0, 9999999, addresses])


def list_wallet_dir():
    pass


def list_wallets():
    pass


def load_wallet():
    pass


def lock_unspent():
    pass


def psbt_bump_fee():
    pass


def remove_pruned_funds():
    pass


def rescan_blockchain():
    pass


def send():
    pass


def send_many():
    pass


def send_to_address():
    pass


def set_hd_seed():
    pass


def set_label():
    pass


def set_tx_fee():
    pass


def set_wallet_flag():
    pass


def sign_message():
    pass


def sign_raw_transaction_with_wallet():
    pass


def unload_wallet():
    pass


def upgrade_wallet():
    pass


def wallet_create_funded_psbt():
    pass


def wallet_lock():
    pass


def wallet_passphrase():
    pass


def wallet_passphrase_change():
    pass


def wallet_process_psbt():
    pass
