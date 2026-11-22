import tkinter as tk
from tkinter import ttk, messagebox


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Универсальный калькулятор — Tkinter')
        self.geometry('460x390')
        self.minsize(420, 360)
        self.configure(bg='#f2f5fa')

        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('App.TFrame', background='#f2f5fa')
        style.configure('App.TLabel', background='#f2f5fa', font=('Arial', 11))
        style.configure('Title.TLabel', background='#f2f5fa', font=('Arial', 18, 'bold'))
        style.configure('Result.TLabel', background='#e3edff', foreground='#183c78',
                        font=('Arial', 14, 'bold'), padding=12)
        style.configure('App.TButton', font=('Arial', 11), padding=8)

        main = ttk.Frame(self, padding=22, style='App.TFrame')
        main.pack(fill='both', expand=True)
        main.columnconfigure(1, weight=1)

        ttk.Label(main, text='Универсальный калькулятор', style='Title.TLabel').grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 18))

        self.first = tk.StringVar()
        self.second = tk.StringVar()
        self.operation = tk.StringVar(value='Сложение (+)')
        self.result = tk.StringVar(value='Результат появится здесь')

        ttk.Label(main, text='Первое число:', style='App.TLabel').grid(row=1, column=0, sticky='w', pady=7)
        self.first_entry = ttk.Entry(main, textvariable=self.first, font=('Arial', 12))
        self.first_entry.grid(row=1, column=1, sticky='ew', pady=7)

        ttk.Label(main, text='Второе число:', style='App.TLabel').grid(row=2, column=0, sticky='w', pady=7)
        ttk.Entry(main, textvariable=self.second, font=('Arial', 12)).grid(row=2, column=1, sticky='ew', pady=7)

        ttk.Label(main, text='Операция:', style='App.TLabel').grid(row=3, column=0, sticky='w', pady=7)
        operations = ['Сложение (+)', 'Вычитание (−)', 'Умножение (×)',
                      'Деление (÷)', 'Возведение в степень (^)']
        ttk.Combobox(main, textvariable=self.operation, values=operations,
                     state='readonly', font=('Arial', 11)).grid(row=3, column=1, sticky='ew', pady=7)

        buttons = ttk.Frame(main, style='App.TFrame')
        buttons.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(20, 16))
        for col in range(3):
            buttons.columnconfigure(col, weight=1)
        ttk.Button(buttons, text='Вычислить', command=self.calculate, style='App.TButton').grid(
            row=0, column=0, sticky='ew', padx=(0, 5))
        ttk.Button(buttons, text='Очистить', command=self.clear, style='App.TButton').grid(
            row=0, column=1, sticky='ew', padx=5)
        ttk.Button(buttons, text='О программе', command=self.about, style='App.TButton').grid(
            row=0, column=2, sticky='ew', padx=(5, 0))

        ttk.Label(main, textvariable=self.result, style='Result.TLabel', anchor='center',
                  wraplength=370).grid(row=5, column=0, columnspan=2, sticky='ew')
        ttk.Label(main, text='Можно вводить десятичные числа через точку или запятую.',
                  style='App.TLabel', wraplength=400).grid(row=6, column=0, columnspan=2,
                                                         sticky='w', pady=(14, 0))
        self.bind('<Return>', lambda event: self.calculate())
        self.first_entry.focus_set()

    def calculate(self):
        try:
            a = float(self.first.get().strip().replace(',', '.'))
            b = float(self.second.get().strip().replace(',', '.'))
        except ValueError:
            messagebox.showerror('Ошибка ввода', 'Введите два корректных числа.')
            return

        op = self.operation.get()
        try:
            if op.startswith('Сложение'):
                value = a + b
            elif op.startswith('Вычитание'):
                value = a - b
            elif op.startswith('Умножение'):
                value = a * b
            elif op.startswith('Деление'):
                if b == 0:
                    messagebox.showerror('Ошибка вычисления', 'На ноль делить нельзя.')
                    return
                value = a / b
            else:
                value = a ** b
                if isinstance(value, complex):
                    messagebox.showerror('Ошибка вычисления', 'Получен комплексный результат.')
                    return
            self.result.set(f'Результат: {value:.10g}')
        except (OverflowError, ValueError, ZeroDivisionError):
            messagebox.showerror('Ошибка вычисления', 'Невозможно вычислить выражение.')

    def clear(self):
        self.first.set('')
        self.second.set('')
        self.operation.set('Сложение (+)')
        self.result.set('Результат появится здесь')
        self.first_entry.focus_set()

    def about(self):
        messagebox.showinfo('О программе',
                            'Универсальный калькулятор на Tkinter.\n'
                            'Поддерживает пять операций и проверку ввода.')


if __name__ == '__main__':
    Calculator().mainloop()
