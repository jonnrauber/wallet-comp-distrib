from bottle import request, post, get, route, jinja2_view, run, redirect, template
import functools
import json
import threading
import time
import sys
from classes import User, Transaction

view = functools.partial(jinja2_view, template_lookup=['views'])

#informações do usuário em pares (nickname, money)
users = [User('admin', 999999)]

#transações de toda a aplicação (src_user, dst_user, money)
transactions = []

@route('/')
@view('index.html')
def home():
    return {'users': users}

@route('/register')
@view('register.html')
def register_page():
    return {}

@get('/users')
@view('users.html')
def list_users_page():
    return {'users': users}

@get('/api/users')
def list_users():
    return json.dumps([user.__dict__ for user in users])

@post('/api/users/new')
def add_user():
    global users
    nickname = request.forms.get('nickname')
    new_user = User(nickname, 0)
    users.append(new_user)
    redirect('/')

@get('/users/<nickname>')
@view('user.html')
def load_user(nickname):
    user = None
    for u in users:
        if u.nickname == nickname:
            user = u
    return {'user': user.__dict__}

@post('/users/<dst_user>/transfer')
def transfer_money(dst_user):
    global users
    value = float(request.forms.get('money'))
    print('${} transferred to user {}'.format(value, dst_user))
    redirect('/users/{}'.format(dst_user))

run(host='localhost', port=int(sys.argv[1]), reloader=True, debug=True)
