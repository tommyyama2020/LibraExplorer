import libra
from canoser import hex_to_int_list
from libra.bytecode import bytecodes
from datetime import datetime, timezone
import pdb

def event_format(ev):
    ev['account'] = ev['event_data_decode']['account']
    ev['account_ab'] = get_address_abbrv_name(ev['account'])
    money = ev['event_data_decode']['amount']
    ev['money'] = money / 1000000


def transaction_format(tx):
    payload = tx['raw_txn']['payload']
    try:
        payload['Script'] = payload.pop('Program')
    except KeyError:
        pass
    sender = tx['raw_txn']['sender']
    tx['sender'] = sender
    tx['sender_ab'] = get_address_abbrv_name(sender)
    if tx['sender_ab'] == "Libra Association":
        tx['sender_text_class'] = 'text-info'
    else:
        tx['sender_text_class'] = 'text-primary'
    try:
        receiver = payload['Script']['args'][0]['Address']
        money = payload['Script']['args'][1]['U64']/1000000
        tx['money'] = money
        tx['receiver'] = receiver
        tx['receiver_ab'] = get_address_abbrv_name(receiver)
        if tx['receiver_ab'] == "Libra Association":
            tx['receiver_text_class'] = 'text-info'
        else:
            tx['receiver_text_class'] = 'text-primary'
    except Exception:
        tx['money'] = "0"
        tx['no_receiver'] = True
    tx['human_time'] = get_human_time(tx['raw_txn']['expiration_time'])
    tx['time'] = get_time_str(tx['raw_txn']['expiration_time'])
    tx['code_name'] = get_tx_abbreviation_name(payload, tx['version'])
    tx['success'] = (tx['transaction_info']['major_status'] == 4001)
    try:
        if len(tx['events']) == 0:
            tx['events_emit'] = 'No Events'
        else:
            tx['events_emit'] = f"{len(tx['events'])} Events"
    except KeyError:
        pass


def get_tx_abbreviation_name(payload, version):
    if version == 0:
        return "Genesis"
    if list(payload)[0] != "Script":
        return list(payload)[0]
    code = hex_to_int_list(payload['Script']['code'])
    if code == bytecodes["mint"]:
        return "mint"
    if code == bytecodes["peer_to_peer_transfer"]:
        return "p2p"
    if code == bytecodes["create_account"]:
        return "new account"
    if code == bytecodes["rotate_authentication_key"]:
        return "rotate key"
    return "script"

def get_address_abbrv_name(address):
    if address == libra.account_config.AccountConfig.association_address():
        return "Libra Association"
    else:
        return address[0:8] + "..." + address[60:64]

def get_human_time(unix_timestamp):
    if unix_timestamp > 2**63:
        return "N/A"
    diff = datetime.now().timestamp() - unix_timestamp
    if diff >= 0:
        suffix = "ago"
    else:
        suffix = "later"
    diff = int(abs(diff)) // 60
    if diff == 0:
        return "just now"
    if diff < 60:
        return f"{diff} mins {suffix}"
    if diff < 60*24:
        return f"{diff//60} hrs {diff%60} mins {suffix}"
    diff = diff // 60
    return f"{diff // 24} day {diff % 24} hrs {suffix}"

def get_time_str(unix_timestamp):
    if unix_timestamp > 2**63:
        return "N/A"
    utc_time = datetime.fromtimestamp(unix_timestamp, timezone.utc)
    local_time = utc_time.astimezone()
    return local_time.strftime("%Y-%m-%d %H:%M:%S %z (%Z)")


def format_metadata(meta):
    meta['start_time_str'] = get_time_str(meta['start_time'])
    meta['latest_time_str'] = get_time_str(meta['latest_time'])

