# -*- coding: utf-8 -*-
"""
Приложение «Учет продаж автозапчастей»
Python + Tkinter + MySQL (mysql-connector-python)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import mysql.connector
from mysql.connector import Error

# ---------- Параметры подключения к MySQL ----------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "впиши_свой_пароль"
DB_NAME = "avtozapchasti"


def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Учет продаж автозапчастей")
        self.geometry("900x600")
        self.resizable(False, False)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self._build_clients_tab()
        self._build_parts_tab()
        self._build_sales_tab()

        # загрузка данных при запуске
        self.load_clients()
        self.load_parts()
        self.load_sales()

        # обновление вкладки при переключении
        self.notebook.bind("<<NotebookChanged>>", self._on_tab_changed)

    # ==================== ОБЩИЙ МЕТОД ВЫПОЛНЕНИЯ ЗАПРОСОВ ====================

    def run_query(self, sql, params=(), fetch=False):
        """Выполняет SQL-запрос с параметрами. Возвращает строки, если fetch=True."""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall() if fetch else None
            conn.commit()
            cur.close()
            conn.close()
            return rows
        except Error as e:
            messagebox.showerror("Ошибка базы данных", str(e))
            return []

    # ==================== ВКЛАДКА КЛИЕНТЫ ====================

    def _build_clients_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Клиенты")

        form = ttk.LabelFrame(frame, text="Данные клиента")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="ФИО:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_client_name = ttk.Entry(form, width=30)
        self.entry_client_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Телефон:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_client_phone = ttk.Entry(form, width=20)
        self.entry_client_phone.grid(row=0, column=3, padx=5, pady=5)

        self.tree_clients = ttk.Treeview(
            frame, columns=("id", "name", "phone"), show="headings", height=12
        )
        self.tree_clients.heading("id", text="ID")
        self.tree_clients.heading("name", text="ФИО")
        self.tree_clients.heading("phone", text="Телефон")
        self.tree_clients.column("id", width=50)
        self.tree_clients.column("name", width=450)
        self.tree_clients.column("phone", width=200)
        self.tree_clients.pack(fill="both", expand=True, padx=10)

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", padx=10, pady=10)

        ttk.Button(buttons, text="Добавить", command=self.add_client).pack(side="left", padx=5)
        ttk.Button(buttons, text="Изменить", command=self.update_client).pack(side="left", padx=5)
        ttk.Button(buttons, text="Удалить", command=self.delete_client).pack(side="left", padx=5)
        ttk.Button(buttons, text="Обновить", command=self.load_clients).pack(side="left", padx=5)

        self.tree_clients.bind("<<TreeviewSelect>>", self._on_client_select)

    def _on_client_select(self, _event):
        sel = self.tree_clients.selection()
        if not sel:
            return
        values = self.tree_clients.item(sel[0])["values"]
        self.entry_client_name.delete(0, tk.END)
        self.entry_client_name.insert(0, values[1])
        self.entry_client_phone.delete(0, tk.END)
        self.entry_client_phone.insert(0, values[2])

    def load_clients(self):
        rows = self.run_query("SELECT id, full_name, phone FROM clients ORDER BY id", fetch=True)
        self.tree_clients.delete(*self.tree_clients.get_children())
        for row in rows or []:
            self.tree_clients.insert("", "end", values=row)

    def add_client(self):
        name = self.entry_client_name.get().strip()
        phone = self.entry_client_phone.get().strip()
        if not name or not phone:
            messagebox.showwarning("Проверка данных", "Заполните ФИО и телефон.")
            return
        self.run_query("INSERT INTO clients (full_name, phone) VALUES (%s, %s)", (name, phone))
        messagebox.showinfo("Успех", "Клиент добавлен.")
        self.load_clients()

    def update_client(self):
        sel = self.tree_clients.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите запись для изменения.")
            return
        client_id = self.tree_clients.item(sel[0])["values"][0]
        name = self.entry_client_name.get().strip()
        phone = self.entry_client_phone.get().strip()
        if not name or not phone:
            messagebox.showwarning("Проверка данных", "Заполните ФИО и телефон.")
            return
        self.run_query(
            "UPDATE clients SET full_name = %s, phone = %s WHERE id = %s",
            (name, phone, client_id),
        )
        messagebox.showinfo("Успех", "Запись обновлена.")
        self.load_clients()

    def delete_client(self):
        sel = self.tree_clients.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите запись для удаления.")
            return
        client_id = self.tree_clients.item(sel[0])["values"][0]
        if not messagebox.askyesno("Подтверждение", "Удалить клиента?"):
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM clients WHERE id = %s", (client_id,))
            conn.commit()
            cur.close()
            conn.close()
        except Error as e:
            messagebox.showerror(
                "Ошибка удаления",
                "Не удалось удалить запись. Сначала удалите связанные продажи.\n" + str(e),
            )
            return
        self.load_clients()

    # ==================== ВКЛАДКА ЗАПЧАСТИ ====================

    def _build_parts_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Запчасти")

        form = ttk.LabelFrame(frame, text="Данные запчасти")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Артикул:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_part_article = ttk.Entry(form, width=15)
        self.entry_part_article.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Наименование:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_part_name = ttk.Entry(form, width=30)
        self.entry_part_name.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Цена:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_part_price = ttk.Entry(form, width=15)
        self.entry_part_price.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Остаток:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_part_stock = ttk.Entry(form, width=15)
        self.entry_part_stock.grid(row=1, column=3, padx=5, pady=5)

        self.tree_parts = ttk.Treeview(
            frame, columns=("id", "article", "name", "price", "stock"),
            show="headings", height=10,
        )
        self.tree_parts.heading("id", text="ID")
        self.tree_parts.heading("article", text="Артикул")
        self.tree_parts.heading("name", text="Наименование")
        self.tree_parts.heading("price", text="Цена")
        self.tree_parts.heading("stock", text="Остаток")
        self.tree_parts.column("id", width=50)
        self.tree_parts.column("article", width=120)
        self.tree_parts.column("name", width=300)
        self.tree_parts.column("price", width=100)
        self.tree_parts.column("stock", width=80)
        self.tree_parts.pack(fill="both", expand=True, padx=10)

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", padx=10, pady=10)

        ttk.Button(buttons, text="Добавить", command=self.add_part).pack(side="left", padx=5)
        ttk.Button(buttons, text="Изменить", command=self.update_part).pack(side="left", padx=5)
        ttk.Button(buttons, text="Удалить", command=self.delete_part).pack(side="left", padx=5)
        ttk.Button(buttons, text="Обновить", command=self.load_parts).pack(side="left", padx=5)

        self.tree_parts.bind("<<TreeviewSelect>>", self._on_part_select)

    def _on_part_select(self, _event):
        sel = self.tree_parts.selection()
        if not sel:
            return
        values = self.tree_parts.item(sel[0])["values"]
        self.entry_part_article.delete(0, tk.END)
        self.entry_part_article.insert(0, values[1])
        self.entry_part_name.delete(0, tk.END)
        self.entry_part_name.insert(0, values[2])
        self.entry_part_price.delete(0, tk.END)
        self.entry_part_price.insert(0, values[3])
        self.entry_part_stock.delete(0, tk.END)
        self.entry_part_stock.insert(0, values[4])

    def load_parts(self):
        rows = self.run_query(
            "SELECT id, article, name, price, stock FROM parts ORDER BY id", fetch=True
        )
        self.tree_parts.delete(*self.tree_parts.get_children())
        for row in rows or []:
            self.tree_parts.insert("", "end", values=row)

    def add_part(self):
        article = self.entry_part_article.get().strip()
        name = self.entry_part_name.get().strip()
        price = self.entry_part_price.get().strip()
        stock = self.entry_part_stock.get().strip()
        if not article or not name or not price or not stock:
            messagebox.showwarning("Проверка данных", "Заполните все поля.")
            return
        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            messagebox.showwarning("Проверка данных", "Цена и остаток должны быть числами.")
            return
        if price < 0 or stock < 0:
            messagebox.showwarning("Проверка данных", "Цена и остаток не могут быть отрицательными.")
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO parts (article, name, price, stock) VALUES (%s, %s, %s, %s)",
                (article, name, price, stock),
            )
            conn.commit()
            cur.close()
            conn.close()
        except Error as e:
            messagebox.showerror("Ошибка базы данных", str(e))
            return
        messagebox.showinfo("Успех", "Запчасть добавлена.")
        self.load_parts()

    def update_part(self):
        sel = self.tree_parts.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите запись для изменения.")
            return
        part_id = self.tree_parts.item(sel[0])["values"][0]
        article = self.entry_part_article.get().strip()
        name = self.entry_part_name.get().strip()
        price = self.entry_part_price.get().strip()
        stock = self.entry_part_stock.get().strip()
        if not article or not name or not price or not stock:
            messagebox.showwarning("Проверка данных", "Заполните все поля.")
            return
        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            messagebox.showwarning("Проверка данных", "Цена и остаток должны быть числами.")
            return
        if price < 0 or stock < 0:
            messagebox.showwarning("Проверка данных", "Цена и остаток не могут быть отрицательными.")
            return
        self.run_query(
            "UPDATE parts SET article = %s, name = %s, price = %s, stock = %s WHERE id = %s",
            (article, name, price, stock, part_id),
        )
        messagebox.showinfo("Успех", "Запись обновлена.")
        self.load_parts()

    def delete_part(self):
        sel = self.tree_parts.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите запись для удаления.")
            return
        part_id = self.tree_parts.item(sel[0])["values"][0]
        if not messagebox.askyesno("Подтверждение", "Удалить запчасть?"):
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM parts WHERE id = %s", (part_id,))
            conn.commit()
            cur.close()
            conn.close()
        except Error as e:
            messagebox.showerror(
                "Ошибка удаления",
                "Не удалось удалить запись. Сначала удалите связанные продажи.\n" + str(e),
            )
            return
        self.load_parts()

    # ==================== ВКЛАДКА ПРОДАЖИ ====================

    def _build_sales_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Продажи")

        form = ttk.LabelFrame(frame, text="Оформление продажи")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="ID клиента:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_sale_client = ttk.Entry(form, width=10)
        self.entry_sale_client.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="ID запчасти:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.entry_sale_part = ttk.Entry(form, width=10)
        self.entry_sale_part.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Количество:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.entry_sale_qty = ttk.Entry(form, width=10)
        self.entry_sale_qty.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(form, text="Дата:").grid(row=0, column=6, padx=5, pady=5, sticky="e")
        self.entry_sale_date = ttk.Entry(form, width=20)
        self.entry_sale_date.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.entry_sale_date.grid(row=0, column=7, padx=5, pady=5)

        search = ttk.LabelFrame(frame, text="Поиск по артикулу и отчет за период")
        search.pack(fill="x", padx=10, pady=5)

        ttk.Label(search, text="Артикул:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_search_article = ttk.Entry(search, width=20)
        self.entry_search_article.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(search, text="Поиск", command=self.search_sales).grid(row=0, column=2, padx=5)

        ttk.Label(search, text="С даты:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_report_from = ttk.Entry(search, width=20)
        self.entry_report_from.grid(row=1, column=1, padx=5, pady=5)
        self.entry_report_from.insert(0, "2020-01-01")

        ttk.Label(search, text="По дату:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_report_to = ttk.Entry(search, width=20)
        self.entry_report_to.grid(row=1, column=3, padx=5, pady=5)
        self.entry_report_to.insert(0, "2030-12-31")

        ttk.Button(search, text="Отчет", command=self.sales_report).grid(row=1, column=4, padx=5)

        ttk.Button(search, text="Все продажи", command=self.load_sales).grid(row=1, column=5, padx=5)

        self.tree_sales = ttk.Treeview(
            frame,
            columns=("id", "article", "name", "qty", "total", "date"),
            show="headings", height=10,
        )
        self.tree_sales.heading("id", text="ID")
        self.tree_sales.heading("article", text="Артикул")
        self.tree_sales.heading("name", text="Наименование")
        self.tree_sales.heading("qty", text="Кол-во")
        self.tree_sales.heading("total", text="Сумма")
        self.tree_sales.heading("date", text="Дата")
        self.tree_sales.column("id", width=50)
        self.tree_sales.column("article", width=110)
        self.tree_sales.column("name", width=250)
        self.tree_sales.column("qty", width=70)
        self.tree_sales.column("total", width=100)
        self.tree_sales.column("date", width=170)
        self.tree_sales.pack(fill="both", expand=True, padx=10)

        self.label_sales_total = ttk.Label(frame, text="")
        self.label_sales_total.pack(anchor="e", padx=10)

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", padx=10, pady=10)

        ttk.Button(buttons, text="Добавить", command=self.add_sale).pack(side="left", padx=5)
        ttk.Button(buttons, text="Изменить", command=self.update_sale).pack(side="left", padx=5)
        ttk.Button(buttons, text="Удалить", command=self.delete_sale).pack(side="left", padx=5)
        ttk.Button(buttons, text="Обновить", command=self.load_sales).pack(side="left", padx=5)

        self.tree_sales.bind("<<TreeviewSelect>>", self._on_sale_select)

    def _on_sale_select(self, _event):
        sel = self.tree_sales.selection()
        if not sel:
            return
        values = self.tree_sales.item(sel[0])["values"]
        self.entry_sale_qty.delete(0, tk.END)
        self.entry_sale_qty.insert(0, values[3])
        self.entry_sale_date.delete(0, tk.END)
        self.entry_sale_date.insert(0, values[5])

    def load_sales(self):
        sql = (
            "SELECT s.id, p.article, p.name, s.quantity, s.total, s.created_at "
            "FROM sales s JOIN parts p ON s.part_id = p.id ORDER BY s.id"
        )
        rows = self.run_query(sql, fetch=True)
        self._fill_sales(rows)
        self.label_sales_total.config(text="")

    def _fill_sales(self, rows):
        self.tree_sales.delete(*self.tree_sales.get_children())
        for row in rows or []:
            self.tree_sales.insert("", "end", values=row)

    def add_sale(self):
        client_id = self.entry_sale_client.get().strip()
        part_id = self.entry_sale_part.get().strip()
        qty = self.entry_sale_qty.get().strip()
        sale_date = self.entry_sale_date.get().strip()
        if not client_id or not part_id or not qty or not sale_date:
            messagebox.showwarning("Проверка данных", "Заполните все поля продажи.")
            return
        try:
            client_id = int(client_id)
            part_id = int(part_id)
            qty = int(qty)
        except ValueError:
            messagebox.showwarning("Проверка данных", "ID и количество должны быть числами.")
            return
        if qty <= 0:
            messagebox.showwarning("Проверка данных", "Количество должно быть больше нуля.")
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT price, stock FROM parts WHERE id = %s", (part_id,))
            part = cur.fetchone()
            if part is None:
                messagebox.showwarning("Проверка данных", "Запчасть с таким ID не найдена.")
                cur.close()
                conn.close()
                return
            price, stock = part
            if qty > stock:
                messagebox.showwarning("Проверка данных", "Количество превышает остаток на складе.")
                cur.close()
                conn.close()
                return
            cur.execute("SELECT id FROM clients WHERE id = %s", (client_id,))
            if cur.fetchone() is None:
                messagebox.showwarning("Проверка данных", "Клиент с таким ID не найден.")
                cur.close()
                conn.close()
                return
            total = float(price) * qty
            # одна транзакция: запись продажи + уменьшение остатка
            cur.execute(
                "INSERT INTO sales (client_id, part_id, quantity, total, created_at) "
                "VALUES (%s, %s, %s, %s, %s)",
                (client_id, part_id, qty, total, sale_date),
            )
            cur.execute("UPDATE parts SET stock = stock - %s WHERE id = %s", (qty, part_id))
            conn.commit()
            cur.close()
            conn.close()
        except Error as e:
            messagebox.showerror("Ошибка базы данных", str(e))
            return
        messagebox.showinfo("Успех", "Продажа оформлена. Сумма: {:.2f} руб.".format(total))
        self.load_parts()
        self.load_sales()

    def update_sale(self):
        sel = self.tree_sales.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите запись для изменения.")
            return
        sale_id = self.tree_sales.item(sel[0])["values"][0]
        qty = self.entry_sale_qty.get().strip()
        sale_date = self.entry_sale_date.get().strip()
        if not qty or not sale_date:
            messagebox.showwarning("Проверка данных", "Заполните количество и дату.")
            return
        try:
            qty = int(qty)
        except ValueError:
            messagebox.showwarning("Проверка данных", "Количество должно быть числом.")
            return
        if qty <= 0:
            messagebox.showwarning("Проверка данных", "Количество должно быть больше нуля.")
            return
        self.run_query(
            "UPDATE sales SET quantity = %s, created_at = %s WHERE id = %s",
            (qty, sale_date, sale_id),
        )
        messagebox.showinfo("Успех", "Запись обновлена.")
        self.load_sales()

    def delete_sale(self):
        sel = self.tree_sales.selection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите запись для удаления.")
            return
        sale_id = self.tree_sales.item(sel[0])["values"][0]
        if not messagebox.askyesno("Подтверждение", "Удалить продажу?"):
            return
        self.run_query("DELETE FROM sales WHERE id = %s", (sale_id,))
        self.load_sales()

    def search_sales(self):
        article = self.entry_search_article.get().strip()
        if not article:
            messagebox.showwarning("Проверка данных", "Введите артикул или его часть.")
            return
        sql = (
            "SELECT s.id, p.article, p.name, s.quantity, s.total, s.created_at "
            "FROM sales s JOIN parts p ON s.part_id = p.id "
            "WHERE p.article LIKE %s"
        )
        rows = self.run_query(sql, ("%" + article + "%",), fetch=True)
        self._fill_sales(rows)
        if not rows:
            messagebox.showinfo("Результат поиска", "Совпадений не найдено.")
        self.label_sales_total.config(text="")

    def sales_report(self):
        date_from = self.entry_report_from.get().strip()
        date_to = self.entry_report_to.get().strip()
        if not date_from or not date_to:
            messagebox.showwarning("Проверка данных", "Укажите начальную и конечную даты.")
            return
        if date_from > date_to:
            messagebox.showwarning("Проверка данных", "Начальная дата больше конечной.")
            return
        sql = (
            "SELECT s.id, p.article, p.name, s.quantity, s.total, s.created_at "
            "FROM sales s JOIN parts p ON s.part_id = p.id "
            "WHERE s.created_at BETWEEN %s AND %s "
            "ORDER BY s.created_at DESC"
        )
        rows = self.run_query(sql, (date_from + " 00:00:00", date_to + " 23:59:59"), fetch=True)
        self._fill_sales(rows)
        total_qty = sum(r[3] for r in rows or [])
        total_sum = sum(float(r[4]) for r in rows or [])
        self.label_sales_total.config(
            text="Продано {} шт. на сумму {:.2f} руб.".format(total_qty, total_sum)
        )
        if not rows:
            messagebox.showinfo("Отчет", "За указанный период продаж нет.")

    # ==================== СЛУЖЕБНОЕ ====================

    def _on_tab_changed(self, _event):
        current = self.notebook.index(self.notebook.select())
        if current == 0:
            self.load_clients()
        elif current == 1:
            self.load_parts()
        elif current == 2:
            self.load_sales()


if __name__ == "__main__":
    app = App()
    app.mainloop()
