class User:
    def __init__(self, nickname, money):
        self.nickname = nickname
        self.money = money
        
    def __str__(self):
        return '{}, ${:.2f}'.format(self.nickname, self.money)
    
    def __repr__(self):
        return '{}, ${:.2f}'.format(self.nickname, self.money)
        
    def withdraw(value):
        self.money -= value
    
    def deposit(value):
        self.money += value
        
        
class Transaction:
    def __init__(self, src_user, src_nickname, value):
        self.src_user = src_user
        self.src_nickname = src_nickname
        self.value = value
        
    def execute():
        try:
            if value < 0:
                raise ValueError('O valor da transação deve ser positivo!')
            if src_user.money - value < 0:
                raise ValueError('Saldo insuficiente para a transação!')
            
            src_user.withdraw(value)
            dst_user.deposit(value)
            self.commit()
        except ValueError as error:
            print('Erro! -> {}'.format(error))
            
    def commit():
        transactions.append(self)
        
