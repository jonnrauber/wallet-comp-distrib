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
Existem duas listas, uma de objetos da classe User e outra de objetos da classe Transaction.
A lista de User contém os nomes de usuário e o valor em suas respectivas carteiras.
A lista de Transaction contém o usuário origem, destino e o valor da transação.
Existem dois usuários pré-carregados na lista, 'jose' com $300.00 e 'maria' com $20.00, só para injetar "dinheiro" na aplicação. A partir destes é possível transferir dinheiro aos demais usuários, até mesmo os que forem criados na página de registro - e que iniciam com $0.00.

## Execução
### Instrução de execução:
```python3 server.py <porta> [vizinho1, vizinho2, ...]```
onde vizinho* é no formato http://<host>:<porta>
  
### Exemplo de execução do programa em três instâncias:
```python3 server.py 8080```
```python3 server.py 8081 http://localhost:8080```
```python3 server.py 8082 http://localhost:8080```
Após algum tempo o host da porta 8082 já deve ter conhecimento da existência do servidor executando na porta 8081.
