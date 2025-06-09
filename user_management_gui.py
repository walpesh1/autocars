import tkinter as tk
from tkinter import messagebox
import sqlite3

def add_user():
    login = entry_login.get()
    pwd = entry_pwd.get()
    role = role_var.get()

    if not login or not pwd:
        messagebox.showerror("Ошибка", "Заполните все поля")
        return

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (login, password_hash, role) VALUES (?, ?, ?)", (login, pwd, role))
        conn.commit()
        messagebox.showinfo("Успех", "Пользователь добавлен")
    except sqlite3.IntegrityError:
        messagebox.showerror("Ошибка", "Пользователь уже существует")

root = tk.Tk()
tk.Label(root, text="Логин").pack()
entry_login = tk.Entry(root)
entry_login.pack()

tk.Label(root, text="Пароль").pack()
entry_pwd = tk.Entry(root, show="*")
entry_pwd.pack()

role_var = tk.StringVar(value="Пользователь")
tk.Radiobutton(root, text="Администратор", variable=role_var, value="Администратор").pack()
tk.Radiobutton(root, text="Пользователь", variable=role_var, value="Пользователь").pack()

tk.Button(root, text="Добавить пользователя", command=add_user).pack()
root.mainloop()