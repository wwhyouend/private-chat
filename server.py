import socket
import threading
import datetime
import random

HOST = '127.0.0.1'
PORT = 12345

clients = []
user_map = {}  # socket -> {'id': ..., 'pseudo': ...}
messages = []
message_id_counter = 0

def generate_user_id():
    return str(random.randint(10**9, 10**10 - 1))

def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode())
        except:
            pass

def send_all_messages():
    for msg in messages:
        formatted = f"[{msg['id']}] {msg['timestamp']} {msg['pseudo']} ({msg['user_id']}): {msg['content']}"
        broadcast(formatted)

def handle_admin_command(command):
    global messages
    parts = command.split(':')
    action = parts[1]

    if action == 'DELETE':
        msg_id = int(parts[2])
        target_msg = next((msg for msg in messages if msg['id'] == msg_id), None)
        if target_msg:
            target_user_id = target_msg['user_id']
            target_pseudo = target_msg['pseudo']
            # Supprimer le message
            messages = [msg for msg in messages if msg['id'] != msg_id]
            # Déconnecter tous les clients avec cet ID
            to_disconnect = [client for client, info in user_map.items() if info['id'] == target_user_id]
            for client in to_disconnect:
                try:
                    client.send("Vous avez été déconnecté par l'administrateur.".encode())
                    client.close()
                except:
                    pass
                if client in clients:
                    clients.remove(client)
                del user_map[client]
            broadcast(f"[ADMIN] Utilisateur {target_pseudo} (ID {target_user_id}) a été déconnecté.")
            send_all_messages()

    elif action == 'EDIT':
        msg_id = int(parts[2])
        new_time = parts[3]
        for msg in messages:
            if msg['id'] == msg_id:
                msg['timestamp'] = new_time
        broadcast(f"[ADMIN] Message {msg_id} modifié à {new_time}.")
        send_all_messages()

    elif action == 'RENAME':
        old_nick = parts[2]
        new_nick = parts[3]
        for msg in messages:
            if msg['pseudo'] == old_nick:
                msg['pseudo'] = new_nick
        for client in user_map:
            if user_map[client]['pseudo'] == old_nick:
                user_map[client]['pseudo'] = new_nick
        broadcast(f"[ADMIN] {old_nick} renommé en {new_nick}.")
        send_all_messages()

def handle_client(client):
    global message_id_counter
    user_id = generate_user_id()
    user_map[client] = {'id': user_id, 'pseudo': None}
    clients.append(client)

    try:
        while True:
            msg = client.recv(1024).decode()
            if msg.startswith("ADMIN:"):
                handle_admin_command(msg)
            if msg.startswith("[ADMIN]"):
                broadcast(msg)
                continue
            else:
                pseudo, content = msg.split(':', 1)
                user_map[client]['pseudo'] = pseudo
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                messages.append({
                    'id': message_id_counter,
                    'user_id': user_map[client]['id'],
                    'pseudo': pseudo,
                    'content': content,
                    'timestamp': timestamp
                })
                formatted = f"[{message_id_counter}] {timestamp} {pseudo} ({user_map[client]['id']}): {content}"
                broadcast(formatted)
                message_id_counter += 1
    except:
        clients.remove(client)
        client.close()
        del user_map[client]

def receive():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Serveur lancé sur {HOST}:{PORT}")
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

receive()