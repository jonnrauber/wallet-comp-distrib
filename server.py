import bottle_session
import requests
from bottle import request, post, get, route, jinja2_view, run, redirect, template, static_file, app
import functools
import json
import threading
import time
import sys
from classes import User, Transaction, ComplexEncoder

app = app()
view = functools.partial(jinja2_view, template_lookup=['views'])
lock = threading.Lock()

#"Vizinhos"
peers = sys.argv[2:]

### Informação a ser compartilhada entre servers ###
#informações do usuário em pares (nickname, money)
users = [User('jose', 300), User('maria', 20)]
#transações de toda a aplicação (src_user, dst_user, money)
transactions = []

#servir arquivos css
@app.get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/')

def special_json(to_view, session):
    index = search_index_by_nickname(session.get('name'))
    if index >= 0:
        to_view['logged_user'] = users[index]
    return to_view

def search_users_by_nickname(nickname):
    return [user for user in users if nickname in user.nickname]

def search_index_by_nickname(nickname):
    for i, user in enumerate(users):
        if nickname == user.nickname:
            return i
    return -1

#API
@app.get('/api/peers')
def list_peers():
    return json.dumps(peers)

@app.get('/api/peers/add')
def i_am_here():
    global peers
    if 'host' in request.query and 'port' in request.query:
        peer = 'http://{}:{}'.format(request.query['host'], request.query['port'])
        if peer not in peers:
            peers.append(peer)
            print('Peer {} adicionado.'.format(peer))

@app.get('/api/users')
def list_users():
    return json.dumps([user.__dict__ for user in users])

@app.get('/api/transactions')
def list_transactions():
    return json.dumps([json.loads(json.dumps(transaction.reprJSON(), cls=ComplexEncoder)) for transaction in transactions])

@app.route('/')
@view('index.html')
def home(session):
    if session.get('name') is None: redirect('/login')
    return special_json({'users': users}, session)

@app.get('/users')
@view('users.html')
def list_users_page(session):
    if session.get('name') is None: redirect('/login')
    list = users
    if 'nickname' in request.query:
        list = search_users_by_nickname(request.query['nickname'])
    return special_json({'users': list}, session)

@app.get('/users/<nickname>')
@view('user.html')
def load_user(session, nickname):
    if session.get('name') is None: redirect('/login')
    if nickname == session.get('name'):
        redirect('/wallet')
    user = None
    for u in users:
        if u.nickname == nickname:
            user = u
    return special_json({'user': user.__dict__}, session)

@app.get('/wallet')
@view('wallet.html')
def load_wallet(session):
    if session.get('name') is None: redirect('/login')
    return special_json({}, session)

@app.get('/transactions')
@view('transactions.html')
def load_transactions_page(session):
    if session.get('name') is None: redirect('/login')
    return special_json({'transactions': transactions[::-1]}, session)

@app.post('/users/<dst_user>/transfer')
def transfer_money(session, dst_user):
    global users
    value = float(request.forms.get('money'))
    try:
        idx_src = search_index_by_nickname(session.get('name'))
        idx_dst = search_index_by_nickname(dst_user)
        if idx_src < 0 or idx_dst < 0:
            raise ValueError('Usuário \'{}\' não encontrado.'.format(user_nickname))
        transaction = Transaction(users[idx_src], users[idx_dst], value)
        transaction.execute()
        transactions.append(transaction)
    except RuntimeError as re:
        print('Erro! {}'.format(re))
        return
    except ValueError as ve:
        print('Erro! -> {}'.format(ve))
    redirect('/users/{}'.format(dst_user))

@app.get('/login')
@view('login.html')
def login_page(session):
    if session.get('name') is not None:
        redirect('/')
    return {}

@app.post('/login')
def login_user(session):
    user_nickname = str(request.forms.get('login'))
    try:
        index = -1
        for idx, user in enumerate(users):
            if user.nickname == user_nickname:
                index = idx
                session['name'] = user_nickname
                break
        if index < 0:
            raise ValueError('Usuário \'{}\' não encontrado.'.format(user_nickname))
    except ValueError as ve:
        print('Erro! {}'.format(ve))
        redirect('/login')
    redirect('/')

@app.get('/signup')
@view('signup.html')
def signup_page(session):
    if session.get('name') is not None:
        redirect('/')
    return {}

@app.post('/signup')
def signup(session):
    user_nickname = str(request.forms.get('login'))
    try:
        for user in users:
            if user.nickname == user_nickname:
                raise ValueError('Usuário \'{}\' já existe.'.format(user_nickname))
        users.append(User(user_nickname, 0))
    except ValueError as ve:
        print('Erro! {}'.format(ve))
        redirect('/signup')
    redirect('/')

@app.get('/logout')
def logout(session):
    session.destroy()
    redirect('/login')


def fault_detector():
    global lock
    time.sleep(3)
    while True:
        time.sleep(3)
        for p in peers:
            if p == 'http://localhost/{}'.format(sys.argv[1]):
                continue
            try:
                r = requests.get('{}/api/peers/add?host={}&port={}'.format(p, 'localhost', sys.argv[1]))
            except requests.exceptions.ConnectionError:
                pass


def refresh_peers():
    global lock
    time.sleep(3)
    while True:
        time.sleep(2)
        np = []
        for p in peers:
            if p == 'http://localhost/{}'.format(sys.argv[1]):
                continue
            try:
                #atualiza peers
                r = requests.get(p + '/api/peers')
                np.append(p)
                np.extend(json.loads(r.text))
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(1)
        with lock:
            peers[:] = list(set(np))
        print('Peers: {}'.format(peers))

def refresh_users():
    global users
    time.sleep(3)
    while True:
        time.sleep(2)
        nu = []
        for p in peers:
            try:
                #atualiza users
                r = requests.get(p + '/api/users')
                nu = nu + json.loads(r.text)
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(1)
        users = update_users(nu)
        print('Usuários: {}'.format(users))

def refresh_transactions():
    global transactions
    time.sleep(3)
    while True:
        time.sleep(2)
        nt = []
        for p in peers:
            try:
                #atualiza transactions
                r = requests.get(p + '/api/transactions')
                nt = nt + json.loads(r.text)
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(1)
        transactions = update_transactions(nt)
        print('Transações: {}'.format(transactions))

def update_users(ngbr_users):
    new_users = users #pega os valores da lista global
    for user_dict in ngbr_users:
        user = User(**user_dict)
        idx_user = search_index_by_nickname(user.nickname)
        if idx_user < 0:
            new_users.append(user)
        else:
            new_users[idx_user] = user
    return new_users

def update_transactions(ngbr_transactions):
    new_transactions = transactions #pega os valores da lista global
    for transaction_dict in ngbr_transactions:
        transaction = Transaction(**transaction_dict)
        if transaction not in new_transactions:
            new_transactions.append(transaction)
    return new_transactions

if __name__ == "__main__":
    session_plugin = bottle_session.SessionPlugin(cookie_lifetime=600)
    app.install(session_plugin)

    t1 = threading.Thread(target=refresh_peers)
    t2 = threading.Thread(target=fault_detector)
    t3 = threading.Thread(target=refresh_users)
    t4 = threading.Thread(target=refresh_transactions)
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    run(app=app, host='localhost', port=int(sys.argv[1]), reloader=False, debug=False)
