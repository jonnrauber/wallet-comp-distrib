class Peer:
    def __init__(self, address):
        self.address = address

    def __str__(self):
        return '<{}>'.format(self.address)

    def __repr__(self):
        return '<{}>'.format(self.address)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.address == other.address
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.address)

class Transaction:
    def __init__(self, peer_origem, peer_destino, valor, vector_clock=None):
        self.peer_origem = peer_origem
        self.peer_destino = peer_destino
        self.valor = valor
        self.vector_clock = vector_clock

    def __str__(self):
        return '${:.2f} transferidos de \'{}\' para \'{}\''.\
            format(self.valor, self.peer_origem, self.peer_destino)

    def __repr__(self):
        return '${:.2f} transferidos de \'{}\' para \'{}\''.\
            format(self.valor, self.peer_origem, self.peer_destino)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.peer_origem == other.peer_origem \
                and self.peer_destino == other.peer_destino \
                and self.valor == other.valor \
                and self.vector_clock == other.vector_clock
        else:
            return False
