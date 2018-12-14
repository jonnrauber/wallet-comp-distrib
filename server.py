import requests
from bottle import request, post, get, route, jinja2_view, run, redirect, template, static_file, app
import functools
import json
import threading
import time
import sys
from classes import Peer, Transaction

app = app()
view = functools.partial(jinja2_view, template_lookup=['views'])
lock = threading.Lock()

#Usuario atual
user = 'http://localhost:' + sys.argv[1]
saldo_inicial = 200
#"Vizinhos"
peers = []
for peer in sys.argv[2:]:
    peers.append(Peer(peer))
#relogio vetorial
vector_clock = {user: 0} # Cria o vector clock inicial (somente o proprio host zerado)
delay_queue = [] #fila de Transaction's

### Informação a ser compartilhada entre servers ###
#transações de toda a aplicação Transaction(peer_origem, peer_destino, valor)
transactions = []

#servir arquivos css e js
@app.get('/<filename:re:.*\.*>')
def stylesheets(filename):
    return static_file(filename, root='static/')

def special_json(to_view):
    to_view['logged_user'] = user
    to_view['saldo'] = calcula_saldo()
    return to_view

def calcula_saldo():
    saldo = saldo_inicial
    for t in transactions:
        if t.peer_origem == user:
            saldo -= t.valor
        if t.peer_destino == user:
            saldo += t.valor
    return saldo

#API
@app.get('/api/peers')
def list_peers():
    peers_addresses = []
    for p in peers:
        peers_addresses.append(p.address)
    return json.dumps(peers_addresses)

@app.get('/api/peers/add')
def i_am_here():
    global peers
    if 'host' in request.query and 'port' in request.query:
        peer = 'http://{}:{}'.format(request.query['host'], request.query['port'])
        ecziste = False
        for p in peers:
            if p.address == peer:
                ecziste = True
                break
        if not ecziste:
            peers.append(Peer(peer))
            vector_clock[peer] = 0
            print('Peer {} adicionado.'.format(peer))

@app.get('/api/transactions')
def list_transactions():
    return json.dumps([transaction.__dict__ for transaction in transactions])

@app.route('/')
@view('base.html')
def home():
    return special_json({'peers': peers, 'transactions': transactions})

def add_transaction(transaction):
    global transactions
    transactions.append(transaction)
    print("Adicionou transação de relógio vetor = {}".format(transaction.vector_clock))
    cmp = functools.cmp_to_key(vector_compare)
    transactions.sort(key=cmp)

@app.post('/transfer')
def transfer_money():
    peer_destino = request.forms.get('peer')
    valor = float(request.forms.get('value'))
    try:
        if valor < 0:
            raise ValueError('O valor da transação deve ser positivo!')
        if valor > calcula_saldo():
            raise ValueError('Não há saldo disponível na carteira!')

        increment_vector_clock()
        transaction = Transaction(user, peer_destino, valor, vector_clock.copy())
        add_transaction(transaction)

    except ValueError as ve:
        print('Erro! -> {}'.format(ve))
    redirect('/')

def increment_vector_clock():
    global vector_clock
    vector_clock[user] += 1

def fault_detector():
    global lock, peers
    time.sleep(3)
    while True:
        time.sleep(3)
        for i in range(len(peers)):
            if peers[i].address == user:
                continue
            try:
                r = requests.get('{}/api/peers/add?host={}&port={}'.format(peers[i].address, 'localhost', sys.argv[1]))
            except requests.exceptions.ConnectionError:
                print("Caiu o peer \'{}\'.".format(peers[i].address))

def refresh_peers():
    global lock
    time.sleep(3)
    while True:
        time.sleep(2)
        np = []
        for p in peers:
            try:
                #atualiza peers
                r = requests.get(p.address + '/api/peers')
                np.append(p)
                for i in json.loads(r.text):
                    if i != user:
                        exists = False
                        for p in peers:
                            if i == p.address:
                                exists = True
                                break
                        if not exists:
                            np.append(Peer(i))
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(1)
        with lock:
            peers[:] = list(set(np))
        for p in peers:
            if p.address not in vector_clock:
                vector_clock[p.address] = 0
        print('Peers: {}'.format(peers))

def refresh_transactions():
    global transactions
    time.sleep(3)
    while True:
        delay_queue[:] = [t for t in delay_queue if t.vector_clock[t.peer_origem] <= vector_clock[t.peer_origem] + 1]

        time.sleep(2)
        for p in peers:
            nt = []
            try:
                #atualiza transactions
                r = requests.get(p.address + '/api/transactions')
                nt = nt + json.loads(r.text)
                update_transactions(nt, p.address)
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(1)

def update_clock(sender_clock):
    global vector_clock
    for key, value in sender_clock.items():
        if key not in vector_clock:
            vector_clock[key] = 0
        vector_clock[key] = max(vector_clock[key],sender_clock[key])

def vector_compare(t1, t2):
    vc1_is_greater = True
    vc1 = t1.vector_clock
    vc2 = t2.vector_clock
    minor = vc1
    if len(vc1) > len(vc2):
        minor = vc2
    for key, value in minor.items():
        if vc1[key] < vc2[key]:
            vc1_is_greater = False
            break
    if vc1_is_greater:
        return -1
    return 1

def update_transactions(ngbr_transactions, ngbr):
    global transactions, vector_clock
    for transaction_dict in ngbr_transactions:
        transaction = Transaction(**transaction_dict)
        exists = False
        for t in transactions:
            if transaction == t:
                exists = True
        if not exists:
            if transaction.peer_origem not in vector_clock:
                vector_clock[transaction.peer_origem] = transaction.vector_clock[transaction.peer_origem] - 1
            if transaction.vector_clock[transaction.peer_origem] <= vector_clock[transaction.peer_origem] + 1:
                #era a transação que esperava receber desse peer
                update_clock(transaction.vector_clock)
                add_transaction(transaction)
            else:
                print("Foram perdidas mensagens do peer {}!".format(transaction.peer_origem))
                #agora eu posso colocar numa fila de espera, com uma thread tentando reinseri-las de tempo em tempo :D
                delay_queue.append(transaction)

if __name__ == "__main__":
    t1 = threading.Thread(target=refresh_peers)
    t2 = threading.Thread(target=fault_detector)
    t3 = threading.Thread(target=refresh_transactions)
    t1.start()
    t2.start()
    t3.start()
    run(app=app, host='localhost', port=int(sys.argv[1]), reloader=False, debug=False)
