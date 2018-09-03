import time
import json

class User:
    def __init__(self, nickname, money):
        self.nickname = nickname
        self.money = money

    def __str__(self):
        return '{} (${:.2f})'.format(self.nickname, self.money)

    def __repr__(self):
        return '{} (${:.2f})'.format(self.nickname, self.money)

    def withdraw(self, value):
        self.money -= value

    def deposit(self, value):
        self.money += value

    def reprJSON(self):
        return dict(nickname=self.nickname, money=self.money)

class Transaction:
    def __init__(self, src_user, dst_user, value, timestamp=time.time()):
        self.src_user = src_user
        self.dst_user = dst_user
        self.value = value
        self.timestamp = timestamp

    def __str__(self):
        return '${:.2f} transferidos de \'{}\' para \'{}\''.\
            format(self.value, self.src_user, self.dst_user)

    def __repr__(self):
        return '${:.2f} transferidos de \'{}\' para \'{}\''.\
            format(self.value, self.src_user, self.dst_user)

    def reprJSON(self):
        return dict(src_user=self.src_user, dst_user=self.dst_user, value=self.value, timestamp=self.timestamp)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.timestamp == other.timestamp \
                    and self.src_user == other.src_user \
                    and self.dst_user == other.dst_user \
                    and self.value == other.value
        else:
            return False

    def execute(self):
        if self.value < 0:
            raise ValueError('O valor da transação deve ser positivo!')
        if self.src_user.money - self.value < 0:
            raise ValueError('Saldo insuficiente para a transação!')

        self.src_user.withdraw(self.value)
        self.dst_user.deposit(self.value)


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)
