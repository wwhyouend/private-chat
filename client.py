import socket
import threading
import tkinter as tk
from tkinter import ttk

HOST = '127.0.0.1'
PORT = 12345

class ClientPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Client Chat")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.pseudo = ""
        self.build_login()

    def build_login(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=50)

        tk.Label(self.login_frame, text="Entrez votre pseudo:").pack()
        self.pseudo_entry = tk.Entry(self.login_frame)
        self.pseudo_entry.pack()
        tk.Button(self.login_frame, text="Connexion", command=self.connect).pack()

    def connect(self):
        self.pseudo = self.pseudo_entry.get()
        if not self.pseudo:
            return
        self.login_frame.destroy()
        self.sock.connect((HOST, PORT))
        self.build_chat()
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def build_chat(self):
        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.chat_frame, columns=('ID', 'Timestamp', 'Pseudo', 'Message'), show='headings')
        for col in ('ID', 'Timestamp', 'Pseudo', 'Message'):
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.entry = tk.Entry(self.root)
        self.entry.pack(fill=tk.X, padx=10, pady=5)
        self.entry.bind("<Return>", self.send_message)

    def send_message(self, event=None):
        content = self.entry.get()
        if content:
            self.sock.send(f"{self.pseudo}:{content}".encode())
            self.entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                msg = self.sock.recv(1024).decode()
                if msg.startswith('['):
                    parts = msg.split(' ', 3)
                    msg_id = parts[0][1:-1]
                    timestamp = parts[1]
                    pseudo = parts[2][:-1]
                    content = parts[3]
                    self.tree.insert('', 'end', values=(msg_id, timestamp, pseudo, content))
                else:
                    self.tree.insert('', 'end', values=("", "", "SYSTEM", msg))
            except:
                break

root = tk.Tk()
app = ClientPanel(root)
root.mainloop()