from bottle import request, post, get, route, jinja2_view, run, redirect, template, static_file
import functools
import json
import threading
import time
import sys
from classes import User, Transaction

view = functools.partial(jinja2_view, template_lookup=['views'])
logged_user = None #informação do usuário logado

"""Informação a ser compartilhada entre servers"""
#informações do usuário em pares (nickname, money)
users = [User('admin', 999999)]
#transações de toda a aplicação (src_user, dst_user, money)
transactions = []

@get('/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/')


def special_json(to_view):
    to_view['logged_user'] = logged_user
    return to_view


def search_users_by_nickname(nickname):
    return [user for user in users if nickname in user.nickname]


@route('/')
@view('index.html')
def home():
    return special_json({'users': users})


@route('/register')
@view('register.html')
def register_page():
    return special_json({})


@get('/users')
@view('users.html')
def list_users_page():
    list = users
    if 'nickname' in request.query:
        list = search_users_by_nickname(request.query['nickname'])
    return special_json({'users': list})


@get('/users/<nickname>')
@view('user.html')
def load_user(nickname):
    if nickname == logged_user.nickname: redirect('/wallet')
    user = None
    for u in users:
        if u.nickname == nickname:
            user = u
    return special_json({'user': user.__dict__})

@get('/wallet')
@view('wallet.html')
def load_wallet():
    return special_json({})


@get('/api/users')
def list_users():
    return special_json(json.dumps([user.__dict__ for user in users]))


@post('/api/users/new')
def add_user():
    global users
    nickname = request.forms.get('nickname')
    new_user = User(nickname, 0)
    users.append(new_user)
    redirect('/')


@post('/users/<dst_user>/transfer')
def transfer_money(dst_user):
    global users
    value = float(request.forms.get('money'))
    print('${} transferred to user {}'.format(value, dst_user))
    redirect('/users/{}'.format(dst_user))


if __name__ == "__main__":
    logged_user = User(str(sys.argv[2]), float((sys.argv[3])))
    users.append(logged_user)
    run(host='localhost', port=int(sys.argv[1]), reloader=True, debug=True)
