import tkinter as tk
from tkinter import messagebox
import sqlite3

def login():
    login = entry_login.get()
    pwd = entry_pwd.get()

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, role, must_change_password FROM Users WHERE login=? AND password_hash=?", (login, pwd))
    result = cursor.fetchone()

    if not result:
        messagebox.showerror("Ошибка", "Неверный логин или пароль")
        return

    user_id, role, must_change = result
    messagebox.showinfo("Успех", "Вы успешно вошли")

    if must_change:
        change_password_window(user_id)

def change_password_window(user_id):
    def change():
        old = entry_old.get()
        new = entry_new.get()
        confirm = entry_confirm.get()

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM Users WHERE id=?", (user_id,))
        current_hash = cursor.fetchone()[0]

        if old != current_hash:
            messagebox.showerror("Ошибка", "Текущий пароль неверен")
            return
        if new != confirm:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return

        cursor.execute("UPDATE Users SET password_hash=?, must_change_password=0 WHERE id=?", (new, user_id))
        conn.commit()
        messagebox.showinfo("Успех", "Пароль изменён")
        window.destroy()

    window = tk.Toplevel()
    tk.Label(window, text="Текущий пароль").pack()
    entry_old = tk.Entry(window, show="*")
    entry_old.pack()

    tk.Label(window, text="Новый пароль").pack()
    entry_new = tk.Entry(window, show="*")
    entry_new.pack()

    tk.Label(window, text="Подтвердите пароль").pack()
    entry_confirm = tk.Entry(window, show="*")
    entry_confirm.pack()

    tk.Button(window, text="Изменить пароль", command=change).pack()

root = tk.Tk()
tk.Label(root, text="Логин").pack()
entry_login = tk.Entry(root)
entry_login.pack()

tk.Label(root, text="Пароль").pack()
entry_pwd = tk.Entry(root, show="*")
entry_pwd.pack()

tk.Button(root, text="Войти", command=login).pack()
root.mainloop()