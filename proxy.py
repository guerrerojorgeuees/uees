import json
from flask import Flask, request, jsonify
from threading import Thread

app = Flask(__name__)
replica_nodes = [
    {'address': ('127.0.0.1', 5015), 'is_leader': True},
    {'address': ('127.0.0.1', 5016), 'is_leader': False},
    {'address': ('127.0.0.1', 5017), 'is_leader': False},
    {'address': ('127.0.0.1', 5018), 'is_leader': False}
]

def get_leader():
    for node in replica_nodes:
        if node['is_leader']:
            return node['address']

def promote_new_leader(new_leader_address):
    for node in replica_nodes:
        if node['address'] == new_leader_address:
            node['is_leader'] = True
        else:
            node['is_leader'] = False

def handle_node_failure(failed_node_address):
    # Implementar lógica para manejar la caída de un nodo
    # Puedes elegir un nuevo líder, iniciar la elección, etc.
    pass

def handle_node_recovery(recovered_node_address):
    # Implementar lógica para manejar la recuperación de un nodo
    # Puedes actualizar su estado, sincronizar datos, etc.
    pass

@app.route('/leader', methods=['GET'])
def get_current_leader():
    leader_address = get_leader()
    return jsonify({'leader': leader_address}), 200

@app.route('/promote_leader', methods=['POST'])
def promote_leader():
    data = request.get_json()
    new_leader_address = tuple(data['new_leader_address'])
    promote_new_leader(new_leader_address)
    return jsonify({'message': f'New leader promoted: {new_leader_address}'}), 200

@app.route('/node_failure', methods=['POST'])
def node_failure():
    data = request.get_json()
    failed_node_address = tuple(data['failed_node_address'])
    handle_node_failure(failed_node_address)
    return jsonify({'message': f'Node failure handled: {failed_node_address}'}), 200

@app.route('/node_recovery', methods=['POST'])
def node_recovery():
    data = request.get_json()
    recovered_node_address = tuple(data['recovered_node_address'])
    handle_node_recovery(recovered_node_address)
    return jsonify({'message': f'Node recovery handled: {recovered_node_address}'}), 200

if __name__ == '__main__':
    app.run(port=5030)
