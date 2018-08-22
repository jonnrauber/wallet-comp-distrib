class User:
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __init__(self, nickname, money):
        self.nickname = nickname
        self.money = money

    def __str__(self):
        return '{}, ${:.2f}'.format(self.nickname, self.money)

    def __repr__(self):
        return '{}, ${:.2f}'.format(self.nickname, self.money)

    def withdraw(self, value):
        self.money -= value

    def deposit(self, value):
        self.money += value


class Transaction:
    def __init__(self, src_user, dst_user, value):
        self.src_user = src_user
        self.dst_user = dst_user
        self.value = value

    def execute(self):
        if self.value < 0:
            raise ValueError('O valor da transação deve ser positivo!')
        if self.src_user.money - self.value < 0:
            raise ValueError('Saldo insuficiente para a transação!')

        self.src_user.withdraw(self.value)
        self.dst_user.deposit(self.value)
