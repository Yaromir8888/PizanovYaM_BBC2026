import math
import sqlite3
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk, messagebox

DB_PATH = Path(__file__).resolve().with_name('calculator.db')
OPERATIONS = ['Сложение (+)', 'Вычитание (−)', 'Умножение (×)', 'Деление (÷)', 'Возведение в степень (^)']


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Калькулятор — Tkinter + SQLite')
        self.geometry('510x430')
        self.minsize(470, 410)
        self.configure(bg='#f2f5fa')
        self.db = sqlite3.connect(DB_PATH)
        self.db.execute('''CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_number REAL NOT NULL,
            second_number REAL NOT NULL,
            operation TEXT NOT NULL,
            result REAL NOT NULL,
            created_at TEXT NOT NULL
        )''')
        self.db.commit()
        self.protocol('WM_DELETE_WINDOW', self.close)

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('App.TFrame', background='#f2f5fa')
        style.configure('App.TLabel', background='#f2f5fa', font=('Arial', 11))
        style.configure('Title.TLabel', background='#f2f5fa', font=('Arial', 18, 'bold'))
        style.configure('Result.TLabel', background='#e3edff', foreground='#183c78',
                        font=('Arial', 14, 'bold'), padding=12)
        style.configure('App.TButton', font=('Arial', 10), padding=8)

        main = ttk.Frame(self, padding=22, style='App.TFrame')
        main.pack(fill='both', expand=True)
        main.columnconfigure(1, weight=1)
        ttk.Label(main, text='Универсальный калькулятор', style='Title.TLabel').grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 18))

        self.first = tk.StringVar()
        self.second = tk.StringVar()
        self.operation = tk.StringVar(value=OPERATIONS[0])
        self.result = tk.StringVar(value='Результат появится здесь')

        ttk.Label(main, text='Первое число:', style='App.TLabel').grid(row=1, column=0, sticky='w', pady=7)
        self.first_entry = ttk.Entry(main, textvariable=self.first, font=('Arial', 12))
        self.first_entry.grid(row=1, column=1, sticky='ew', pady=7)
        ttk.Label(main, text='Второе число:', style='App.TLabel').grid(row=2, column=0, sticky='w', pady=7)
        ttk.Entry(main, textvariable=self.second, font=('Arial', 12)).grid(row=2, column=1, sticky='ew', pady=7)
        ttk.Label(main, text='Операция:', style='App.TLabel').grid(row=3, column=0, sticky='w', pady=7)
        ttk.Combobox(main, textvariable=self.operation, values=OPERATIONS,
                     state='readonly', font=('Arial', 11)).grid(row=3, column=1, sticky='ew', pady=7)

        buttons = ttk.Frame(main, style='App.TFrame')
        buttons.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(18, 12))
        for col in range(2):
            buttons.columnconfigure(col, weight=1)
        ttk.Button(buttons, text='Вычислить и сохранить', command=self.calculate,
                   style='App.TButton').grid(row=0, column=0, sticky='ew', padx=4, pady=4)
        ttk.Button(buttons, text='История (SQL)', command=self.show_history,
                   style='App.TButton').grid(row=0, column=1, sticky='ew', padx=4, pady=4)
        ttk.Button(buttons, text='Очистить поля', command=self.clear,
                   style='App.TButton').grid(row=1, column=0, sticky='ew', padx=4, pady=4)
        ttk.Button(buttons, text='О программе', command=self.about,
                   style='App.TButton').grid(row=1, column=1, sticky='ew', padx=4, pady=4)

        ttk.Label(main, textvariable=self.result, style='Result.TLabel', anchor='center',
                  wraplength=430).grid(row=5, column=0, columnspan=2, sticky='ew')
        ttk.Label(main, text='Вводите числа через точку или запятую. Вычисления сохраняются в SQLite.',
                  style='App.TLabel', wraplength=450).grid(row=6, column=0, columnspan=2,
                                                         sticky='w', pady=(14, 0))
        self.bind('<Return>', lambda event: self.calculate())
        self.first_entry.focus_set()

    def calculate(self):
        try:
            a = float(self.first.get().strip().replace(',', '.'))
            b = float(self.second.get().strip().replace(',', '.'))
            if not (math.isfinite(a) and math.isfinite(b)):
                raise ValueError
        except ValueError:
            messagebox.showerror('Ошибка ввода', 'Введите два корректных конечных числа.', parent=self)
            return
        op = self.operation.get()
        try:
            if op == OPERATIONS[0]:
                value = a + b
            elif op == OPERATIONS[1]:
                value = a - b
            elif op == OPERATIONS[2]:
                value = a * b
            elif op == OPERATIONS[3]:
                if b == 0:
                    raise ZeroDivisionError
                value = a / b
            elif op == OPERATIONS[4]:
                value = a ** b
            else:
                raise ValueError
            if isinstance(value, complex) or not math.isfinite(value):
                raise ValueError
        except (OverflowError, ValueError, ZeroDivisionError):
            messagebox.showerror('Ошибка вычисления', 'Невозможно вычислить выражение (проверьте операцию и делитель).', parent=self)
            return
        try:
            with self.db:
                self.db.execute('''INSERT INTO calculations
                    (first_number, second_number, operation, result, created_at)
                    VALUES (?, ?, ?, ?, ?)''',
                    (a, b, op, value, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        except sqlite3.Error as exc:
            messagebox.showerror('Ошибка SQL', f'Не удалось сохранить вычисление:\n{exc}', parent=self)
            return
        self.result.set(f'Результат: {value:.10g}  ✓ сохранено в SQL')

    def clear(self):
        self.first.set('')
        self.second.set('')
        self.operation.set(OPERATIONS[0])
        self.result.set('Результат появится здесь')
        self.first_entry.focus_set()

    def show_history(self):
        window = tk.Toplevel(self)
        window.title('История вычислений — SQLite')
        window.geometry('850x430')
        window.minsize(650, 320)
        window.transient(self)
        frame = ttk.Frame(window, padding=12)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='История вычислений (двойной щелчок — повторить)',
                  font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 8))
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill='both', expand=True)
        cols = ('id', 'date', 'a', 'op', 'b', 'result')
        tree = ttk.Treeview(table_frame, columns=cols, show='headings', selectmode='browse')
        headings = ['ID', 'Дата и время', 'Число 1', 'Операция', 'Число 2', 'Результат']
        widths = [45, 155, 105, 200, 105, 110]
        for col, heading, width in zip(cols, headings, widths):
            tree.heading(col, text=heading)
            tree.column(col, width=width, minwidth=45, anchor='center')
        scroll = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

        def refresh():
            for item in tree.get_children():
                tree.delete(item)
            try:
                rows = self.db.execute('''SELECT id, created_at, first_number, operation,
                                              second_number, result
                                       FROM calculations ORDER BY id DESC''').fetchall()
                for row in rows:
                    tree.insert('', 'end', values=row)
            except sqlite3.Error as exc:
                messagebox.showerror('Ошибка SQL', str(exc), parent=window)

        def selected_id():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning('Выбор записи', 'Сначала выберите запись в таблице.', parent=window)
                return None
            return int(tree.item(selected[0], 'values')[0])

        def delete_selected():
            record_id = selected_id()
            if record_id is None:
                return
            if messagebox.askyesno('Подтверждение', 'Удалить выбранную запись?', parent=window):
                try:
                    with self.db:
                        self.db.execute('DELETE FROM calculations WHERE id = ?', (record_id,))
                    refresh()
                except sqlite3.Error as exc:
                    messagebox.showerror('Ошибка SQL', str(exc), parent=window)

        def clear_history():
            if not messagebox.askyesno('Подтверждение', 'Удалить ВСЮ историю вычислений?', parent=window):
                return
            try:
                with self.db:
                    self.db.execute('DELETE FROM calculations')
                refresh()
            except sqlite3.Error as exc:
                messagebox.showerror('Ошибка SQL', str(exc), parent=window)

        def load_selected(event=None):
            record_id = selected_id()
            if record_id is None:
                return
            try:
                row = self.db.execute('''SELECT first_number, second_number, operation
                                         FROM calculations WHERE id = ?''', (record_id,)).fetchone()
            except sqlite3.Error as exc:
                messagebox.showerror('Ошибка SQL', str(exc), parent=window)
                return
            if row:
                self.first.set(str(row[0]))
                self.second.set(str(row[1]))
                self.operation.set(row[2])
                self.result.set('Нажмите «Вычислить и сохранить»')
                window.destroy()
                self.first_entry.focus_set()

        tree.bind('<Double-1>', load_selected)
        actions = ttk.Frame(frame)
        actions.pack(fill='x', pady=(10, 0))
        ttk.Button(actions, text='Повторить', command=load_selected).pack(side='left', padx=4)
        ttk.Button(actions, text='Удалить выбранное', command=delete_selected).pack(side='left', padx=4)
        ttk.Button(actions, text='Очистить историю', command=clear_history).pack(side='left', padx=4)
        ttk.Button(actions, text='Обновить', command=refresh).pack(side='right', padx=4)
        refresh()

    def about(self):
        messagebox.showinfo('О программе',
                            'Универсальный калькулятор на Tkinter с базой SQLite.\n'
                            'Поддерживает пять операций, проверку ввода,\n'
                            'сохранение, просмотр и удаление истории.\n\n'
                            f'База данных: {DB_PATH}', parent=self)

    def close(self):
        self.db.close()
        self.destroy()


if __name__ == '__main__':
    Calculator().mainloop()
