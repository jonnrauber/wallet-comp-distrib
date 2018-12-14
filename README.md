# wallet-comp-distrib
Projeto de aplicativo para pagamentos.
Atualmente implementado no formato cliente-servidor.

## Requisitos
### bottle
```sudo python3 -m pip install bottle```
### bottle-session
```sudo python3 -m pip install bottle-session```
### redis-server
```sudo apt install redis-server```
## Funcionamento
Ao iniciar um client, o usuário é criado com o nick 'http://localhost:' + {a porta do processo do client}.
Esse usuário inicia com 200 de saldo.
Os peers vizinhos são passados como argumento na execução.
Uma Transaction contém o usuário origem, destino, valor da transação e um relógio vetor para ordenação.
Quando um usuário envia dinheiro para outro, este cria uma transação e incrementa o relógio vetor.
Quando os usuários recebem uma nova transação, são capazes de verificar pelo relógio vetor se foi perdida uma transação anterior (nesse caso exibe mensagem no terminal do client). Também o relógio vetor é o responsável pela correta ordenação das transações na tela inicial exibida no navegador web.

## Execução
### Instrução de execução:
```python3 server.py <porta> [vizinho1, vizinho2, ...]```
onde vizinho* é no formato http://<host>:<porta>
  
### Exemplo de execução do programa em três instâncias:
```python3 server.py 8080```
```python3 server.py 8081 http://localhost:8080```
```python3 server.py 8082 http://localhost:8080```
Após algum tempo o host da porta 8082 já deve ter conhecimento da existência do servidor executando na porta 8081.
