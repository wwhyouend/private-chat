import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime

HOST = '127.0.0.1'
PORT = 12345

ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "1234"

class AdminPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Authentification Admin")
        self.login_screen()

    def login_screen(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=50)

        tk.Label(self.login_frame, text="Login:").grid(row=0, column=0)
        self.login_entry = tk.Entry(self.login_frame)
        self.login_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Mot de passe:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.login_frame, text="Connexion", command=self.authenticate).grid(row=2, column=0, columnspan=2)

    def authenticate(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        if login == ADMIN_LOGIN and password == ADMIN_PASSWORD:
            self.login_frame.destroy()
            self.build_panel()
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects.")

    def build_panel(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        self.tree = ttk.Treeview(self.root, columns=('ID', 'Timestamp', 'Pseudo', 'Message'), show='headings')
        for col in ('ID', 'Timestamp', 'Pseudo', 'Message'):
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        cmd_frame = tk.Frame(self.root)
        cmd_frame.pack(pady=10)

        # Envoi de message admin
        send_frame = tk.Frame(self.root)
        send_frame.pack(pady=10)

        tk.Label(send_frame, text="Message admin:").pack(side=tk.LEFT)
        self.admin_msg_entry = tk.Entry(send_frame, width=50)
        self.admin_msg_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(send_frame, text="Envoyer", command=self.send_admin_message).pack(side=tk.LEFT)

        # Suppression
        tk.Label(cmd_frame, text="ID à supprimer:").grid(row=0, column=0)
        self.delete_entry = tk.Entry(cmd_frame)
        self.delete_entry.grid(row=0, column=1)
        tk.Button(cmd_frame, text="Supprimer", command=self.delete_message).grid(row=0, column=2)

        # Modification date/heure
        tk.Label(cmd_frame, text="ID à modifier:").grid(row=1, column=0)
        self.edit_id_entry = tk.Entry(cmd_frame)
        self.edit_id_entry.grid(row=1, column=1)
        tk.Label(cmd_frame, text="Nouvelle date/heure:").grid(row=1, column=2)
        self.edit_time_entry = tk.Entry(cmd_frame)
        self.edit_time_entry.grid(row=1, column=3)
        tk.Button(cmd_frame, text="Modifier", command=self.edit_timestamp).grid(row=1, column=4)

        # Renommage pseudo
        tk.Label(cmd_frame, text="Ancien pseudo:").grid(row=2, column=0)
        self.old_nick_entry = tk.Entry(cmd_frame)
        self.old_nick_entry.grid(row=2, column=1)
        tk.Label(cmd_frame, text="Nouveau pseudo:").grid(row=2, column=2)
        self.new_nick_entry = tk.Entry(cmd_frame)
        self.new_nick_entry.grid(row=2, column=3)
        tk.Button(cmd_frame, text="Renommer", command=self.rename_user).grid(row=2, column=4)

        # Rafraîchir / Exporter
        tk.Button(cmd_frame, text="🔁 Rafraîchir", command=self.refresh_messages).grid(row=3, column=0)
        tk.Button(cmd_frame, text="📤 Exporter", command=self.export_messages).grid(row=3, column=1)

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_admin_message(self):
        content = self.admin_msg_entry.get()
        if content:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            formatted = f"[ADMIN] {timestamp} Admin: {content}"
            try:
                self.sock.send(formatted.encode())
            except:
                messagebox.showerror("Erreur", "Impossible d'envoyer le message.")
            self.admin_msg_entry.delete(0, tk.END)

    def delete_message(self):
        msg_id = self.delete_entry.get()
        self.sock.send(f"ADMIN:DELETE:{msg_id}".encode())

    def edit_timestamp(self):
        msg_id = self.edit_id_entry.get()
        new_time = self.edit_time_entry.get()
        self.sock.send(f"ADMIN:EDIT:{msg_id}:{new_time}".encode())

    def rename_user(self):
        old_nick = self.old_nick_entry.get()
        new_nick = self.new_nick_entry.get()
        self.sock.send(f"ADMIN:RENAME:{old_nick}:{new_nick}".encode())

    def refresh_messages(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def export_messages(self):
        with open("messages_export.txt", "w", encoding="utf-8") as f:
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                f.write(f"[{values[0]}] {values[1]} {values[2]}: {values[3]}\n")
        messagebox.showinfo("Export", "Messages exportés dans messages_export.txt")

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
            except:
                break

root = tk.Tk()
app = AdminPanel(root)
root.mainloop()