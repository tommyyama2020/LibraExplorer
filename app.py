from flask import Flask, flash, redirect, render_template, render_template_string, request, session, abort
from flask import jsonify
import werkzeug
from flask_babel import Babel
from flask_babel import _
import json
import os
import requests
from view_helper import *
import pdb

def is_development():
    try:
        return os.environ["FLASK_ENV"] == "development"
    except Exception:
        return False

def is_devnet(host):
    return host.lower().startswith("devnet.")

def is_prefix_network(is_development, host, pack_suffix=False):
    host = host.lower()
    if is_development:
        suffix = ".localhost:5000"
    else:
        suffix = ".explorer.moveonlibra.com"
    is_anonymous = host.endswith(suffix)
    if pack_suffix:
        return (is_anonymous, suffix)
    else:
        return is_anonymous

def is_anonymous_network(is_development, host):
    return is_prefix_network(is_development, host) and not is_devnet(host)

def get_network_prefix(is_development, host):
    anonymous_network, suffix = is_prefix_network(is_development, host, True)
    if anonymous_network:
        endlen = -len(suffix)
        return host[0:endlen]
    else:
        raise f"{host} is not a anonymous network."

def gen_api_header(is_development, host):
    api_header = {}
    anonymous_network = is_prefix_network(is_development, host)
    if is_prefix_network(is_development, host):
        api_header["RealSwarm"] = get_network_prefix(is_development, host)
    if False and is_development:
        if is_devnet(host):
            appkey = "eyJhbGciOiJIUzUxMiJ9.eyJkYXRhIjoiZHgxeHR4M3h1IiwiaWF0IjoxNTc0MTQyMjgwLCJleHAiOjE4ODk1MDIyODB9.wvODMtecFuYne92tmy5khn2NFd_D4RFILg0ws1LGXrdTjX-2JU58WiWdA1FK6pf5ylXb8LUjXR3JO5hDs561Bw"
        else:
            appkey = "eyJhbGciOiJIUzUxMiJ9.eyJkYXRhIjoidHgxeHR4M3hzIiwiaWF0IjoxNTc0MDcwMDc5LCJleHAiOjE4ODk0MzAwNzl9.BtS492nhSMK9zjEsFhIhsruGh2W9g8lSqAc_FXhFkY7R44-2MS2d8mOkqUDQXJGqOvD4mRTRXb0eEy4bhDgCbA"
    else:
        if is_devnet(host):
            appkey = "eyJhbGciOiJIUzUxMiJ9.eyJkYXRhIjoiZHgxeHR4M3h1IiwiaWF0IjoxNTc0MDgwNjQ4LCJleHAiOjE4ODk0NDA2NDh9.X5Jpo8fkOpC2H7uUjRShcVozph7APs3cGs3W9YmLwEfSMk7X0sEcGFLW-6P4EBujOsrP-b158xD_-LdNdpYKvg"
        else:
            appkey = "eyJhbGciOiJIUzUxMiJ9.eyJkYXRhIjoidHgxeHl4MXh1IiwiaWF0IjoxNTcyOTI0NzQxLCJleHAiOjE2MDQ0NjA3NDF9.2yh_gbH266nWHQ9E_fghs7vVoFHT7a1Z6Zi-NEYt7VTmzK8GPG7BzrBkJ3HATCoVFawss_tLMqqHRUtsGVkJSQ"
    api_header["Authorization"] = f"Bearer {appkey}"
    return api_header

def jwt_header():
    return gen_api_header(is_development(), request.host.lower())


def api_host():
    if is_development():
        return "http://apitest.MoveOnLibra.com"
        return "http://localhost:8000"
    else:
        return "http://apitest.MoveOnLibra.com"

def move_on_libra_api(url, params={}, get_method=True):
    host = api_host()
    def do_api():
        if get_method:
            r = requests.get(host+url, params=params, headers=jwt_header())
        else:
            r = requests.post(host+url, params=params, headers=jwt_header())
        return r
    #
    try:
        r = do_api()
        if r.status_code == 500:
            print("retry on 500")
            r = do_api()
    except Exception as err:
        flash(_("Can't finish your request:") + f"\n{err}")
        abort(500)
    if r.status_code == 404:
        return None
    if r.status_code != 200:
        flash(_("Can't finish your request:") + _(" API server return an error response: ") + f"{r.status_code}\n{r.text}")
        abort(500)
    update_total(int(r.headers["Latest-Version"])+1)
    data = json.loads(r.content.decode('utf-8-sig'))
    return data

def get_txs(start, limit=20):
    url = "/v1/transactions"
    params = {"limit": limit, "start_version": start}
    return move_on_libra_api(url, params)

def get_latest_txs(limit=10):
    url = "/v1/transactions/latest"
    params = {"limit": limit}
    return move_on_libra_api(url, params)

def get_transaction(id):
    url = "/v1/transactions/"+str(id)
    return move_on_libra_api(url)


def get_account(address):
    url = "/v1/address/"+address
    return move_on_libra_api(url)

def get_account_latest_events(address):
    url = "/v1/events/latest/"+address
    params = {"limit": 5}
    return move_on_libra_api(url, params)

def post_mint(address):
    url = "/v1/transactions/mint"
    params = {"number_of_micro_libra": 100000000, "receiver_account_address": address}
    return move_on_libra_api(url, params, get_method=False)

def get_validators():
    url = "/v1/libra/validators"
    return move_on_libra_api(url)

def get_metadata():
    url = "/v1/libra/about"
    return move_on_libra_api(url)


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/@MoveOnLibra'
app.config['JSON_SORT_KEYS'] = False
app.config['LANGUAGES'] = ['en', 'zh', 'zh_Hant', 'ar', 'da', 'de', 'el', 'es', 'fa', 'fr', 'ga', 'it', 'ja', 'ko', 'nl', 'pt', 'ru', 'sr', 'sv', 'th', 'tr']

babel = Babel(app)

@babel.localeselector
def get_locale():
    # print(request.accept_languages)
    # print(request.accept_languages.best_match(app.config['LANGUAGES']))
    try:
        lang, _ = request.accept_languages[0]
        if 'zh' in lang.lower():
            if 'tw' in lang.lower() or 'hk' in lang.lower():
                return 'zh_Hant'
    except:
        pass
    return request.accept_languages.best_match(app.config['LANGUAGES'])


total = 1

def update_total(new_total):
    global total
    total = new_total


@app.route("/")
def index():
    latest_txs = get_latest_txs(20)
    for tx in latest_txs:
        transaction_format(tx)
    meta = get_metadata()
    format_metadata(meta)
    meta['latest_start'] = latest_txs[-1]['version']
    return render_template('index.html',txs=latest_txs, meta=meta)

@app.route("/test")
def test():
    return render_template('test.html')

@app.route("/latest_txs")
def load_latest_txs():
    limit = 20
    start = request.args.get('start', '0')
    start = int(start)
    if start + limit <=0:
        return render_template_string("")
    if start < 0:
        limit = limit + start
        start = 0
    txs = get_txs(start, limit=limit)
    for tx in txs:
        transaction_format(tx)
    txs.reverse()
    return render_template('_txs.html',txs=txs)

@app.route("/transactions")
def transactions():
    start = request.args.get('start', '0')
    limit = 20
    txs = get_txs(start, limit=limit)
    for tx in txs:
        transaction_format(tx)
    cur = txs[0]["version"]
    ctx={'first_class': '', 'last_class': ''}
    total_page = total//limit
    cur_page = cur//limit
    ctx['total'] = total
    ctx['total_page'] = total_page
    ctx['cur_page'] = cur_page
    ctx['limit'] = limit
    if cur_page == 0:
        ctx['first_class'] = 'disabled'
    if cur_page == total_page:
        ctx['last_class'] = 'disabled'
    return render_template('transactions.html',txs=txs, ctx=ctx)

@app.route("/transactions/<int:id>")
def transaction(id):
    tx = get_transaction(id)
    if tx is None:
        flash(_('Transaction Not Found: %(id)s', id=id))
        return redirect("/")
    raw_json = json.dumps(tx, indent=2)
    transaction_format(tx)
    tx['raw_json'] = raw_json
    ctx={'first_class': '', 'last_class': ''}
    ctx['total'] = total
    if id <= 0:
        ctx['first_class'] = 'disabled'
    if id >= total-1:
        ctx['last_class'] = 'disabled'
    return render_template('transaction_show.html',tx=tx, ctx=ctx)

@app.route("/transactions/<int:id>.json")
def transaction_json(id):
    tx = get_transaction(id)
    return jsonify(tx)

@app.route("/accounts")
def accounts():
    validators = get_validators()
    return render_template('accounts.html', validators=enumerate(validators),
        core_code_address='0000000000000000000000000000000000000000000000000000000000000000',
        association_address='000000000000000000000000000000000000000000000000000000000a550c18',
        transaction_fee_address='0000000000000000000000000000000000000000000000000000000000000fee',
        validator_set_address='00000000000000000000000000000000000000000000000000000000000001d8'
        )


@app.route("/accounts/<string:address>")
def account(address):
    acc = get_account(address)
    if acc is None:
        flash(_('Address Not Found: %(address)s', address=address))
        return render_template('account_404.html',address=address)
    raw_json = json.dumps(acc, indent=2)
    try:
        events = get_account_latest_events(address)
        for ev in events['sent']:
            event_format(ev)
        for ev in events['received']:
            event_format(ev)
        acc['events'] = events
    except Exception:
        #TODO: Request failed DB corrupt: Sequence number not continuous, expected: 0, actual: 1.
        acc['events'] = {'sent':[], 'received':[]}
    acc['raw_json'] = raw_json
    #TODO: 404
    return render_template('account_show.html',acc=acc)


@app.route("/accounts/<string:address>.json")
def account_json(address):
    acc = get_account(address)
    return jsonify(acc)


@app.route("/transactions/mint/<string:address>", methods=['POST'])
def mint(address):
    if is_anonymous_network(is_development(), request.host):
        flash(_('Anonymous network can not mint coins.'))
    else:
        post_mint(address)
    return redirect(f"/accounts/{address}")

@app.route("/search")
def search():
    query = request.args.get('q', '')
    if len(query)==64:
        return redirect(f"/accounts/{query}")
    try:
        version = int(query)
        return redirect(f"/transactions/{version}")
    except Exception:
        flash(_("Can't finish your search rquest") + _(", maybe the query string %(query)s is malformed.", query=query))
        return redirect("/")

@app.route('/heartbeat/<int:id>')
def heartbeat(id):
    return jsonify(id)

@app.errorhandler(werkzeug.exceptions.HTTPException)
def handle_exception(e):
    return render_template('error.html'), 500

@app.context_processor
def inject_network():
    if is_devnet(request.host):
        network = "Devnet"
        network_address = "apitest.moveonLibra.com"
        network_port = "33333"
    elif is_anonymous_network(is_development(), request.host):
        network = "Anonymous"
        prefix = get_network_prefix(is_development(), request.host)
        network_address, network_port = prefix.split("-")
    else:
        network = "Testnet"
        network_address = "ac.testnet.libra.org"
        network_port = "8000"
    return dict(network=network, network_address=network_address, network_port=network_port)

@app.teardown_appcontext
def shutdown_session(exception=None):
    #print("teardown_appcontext")
    pass

@app.teardown_request
def show_teardown(exception):
    #print('teardown_request')
    pass

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=False)