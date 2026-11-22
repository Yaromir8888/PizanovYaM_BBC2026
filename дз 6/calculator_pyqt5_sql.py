import sys
import sqlite3
import math
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox, QPushButton,
    QMessageBox, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QTabWidget
)

DB_PATH = Path(__file__).resolve().parent / 'calculator.db'


class Database:
    def __init__(self, path=DB_PATH):
        self.connection = sqlite3.connect(str(path))
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_number REAL NOT NULL,
                second_number REAL NOT NULL,
                operation_index INTEGER NOT NULL,
                operation_symbol TEXT NOT NULL,
                result REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
        ''')
        self.connection.commit()
        self.migrate_schema()

    def migrate_schema(self):
        """Обновить старую базу без удаления сохранённых вычислений."""
        columns = {row[1] for row in self.connection.execute('PRAGMA table_info(calculations)')}
        additions = {
            'operation_symbol': "TEXT NOT NULL DEFAULT '?'",
            'operation_index': 'INTEGER NOT NULL DEFAULT 0',
            'created_at': "TEXT NOT NULL DEFAULT ''",
        }
        with self.connection:
            for name, definition in additions.items():
                if name not in columns:
                    self.connection.execute(f'ALTER TABLE calculations ADD COLUMN {name} {definition}')
            self.connection.execute("""
                UPDATE calculations
                SET operation_symbol = CASE operation_index
                    WHEN 0 THEN '+' WHEN 1 THEN '−' WHEN 2 THEN '×'
                    WHEN 3 THEN '÷' WHEN 4 THEN '^' ELSE '?'
                END
                WHERE operation_symbol IS NULL OR operation_symbol = '?'
            """)
            self.connection.execute("""
                UPDATE calculations SET created_at = datetime('now', 'localtime')
                WHERE created_at IS NULL OR created_at = ''
            """)

    def add(self, a, b, operation_index, sign, result):
        with self.connection:
            self.connection.execute('''
                INSERT INTO calculations
                (first_number, second_number, operation_index, operation_symbol, result)
                VALUES (?, ?, ?, ?, ?)
            ''', (a, b, operation_index, sign, result))

    def all(self):
        return self.connection.execute('''
            SELECT id, created_at, first_number, operation_symbol,
                   second_number, result, operation_index
            FROM calculations ORDER BY id DESC
        ''').fetchall()

    def delete(self, record_id):
        with self.connection:
            self.connection.execute('DELETE FROM calculations WHERE id = ?', (record_id,))

    def clear(self):
        with self.connection:
            self.connection.execute('DELETE FROM calculations')

    def close(self):
        self.connection.close()


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Универсальный калькулятор — PyQt5 + SQLite')
        self.resize(760, 570)
        self.db = Database()
        self.create_ui()
        self.refresh_history()

    def create_ui(self):
        self.setStyleSheet('''
            QWidget { background: #f4f6fb; color: #1f2937; font-size: 14px; }
            QLineEdit, QComboBox, QTableWidget { background: white; border: 1px solid #cbd5e1;
                border-radius: 7px; padding: 6px; }
            QLineEdit:focus, QComboBox:focus { border: 2px solid #2563eb; }
            QPushButton { background: #2563eb; color: white; border: none;
                border-radius: 7px; padding: 11px; font-weight: bold; }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton#clear { background: #64748b; }
            QPushButton#clear:hover { background: #475569; }
            QPushButton#danger { background: #b91c1c; }
            QPushButton#danger:hover { background: #991b1b; }
            QGroupBox { border: 1px solid #cbd5e1; border-radius: 9px;
                margin-top: 12px; padding: 15px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 5px; }
            QTabWidget::pane { border: 1px solid #cbd5e1; border-radius: 7px; }
        ''')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        heading = QLabel('Универсальный калькулятор')
        heading.setAlignment(Qt.AlignCenter)
        heading.setStyleSheet('font-size: 22px; font-weight: bold; color: #1e40af;')
        layout.addWidget(heading)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        calc_tab = QWidget()
        calc_layout = QVBoxLayout(calc_tab)
        calc_layout.setSpacing(14)
        description = QLabel('Введите два числа и выберите математическую операцию.')
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        calc_layout.addWidget(description)
        form = QFormLayout()
        form.setSpacing(12)
        self.first = QLineEdit()
        self.first.setPlaceholderText('Например, 12.5')
        self.second = QLineEdit()
        self.second.setPlaceholderText('Например, 2')
        self.operation = QComboBox()
        self.operation.addItems(['Сложение (+)', 'Вычитание (−)', 'Умножение (×)',
                                 'Деление (÷)', 'Возведение в степень (^)'])
        form.addRow('Первое число:', self.first)
        form.addRow('Второе число:', self.second)
        form.addRow('Операция:', self.operation)
        calc_layout.addLayout(form)
        buttons = QHBoxLayout()
        calculate = QPushButton('Вычислить')
        calculate.clicked.connect(self.calculate)
        clear = QPushButton('Очистить')
        clear.setObjectName('clear')
        clear.clicked.connect(self.clear_fields)
        about = QPushButton('О программе')
        about.clicked.connect(self.show_about)
        for button in (calculate, clear, about):
            buttons.addWidget(button)
        calc_layout.addLayout(buttons)
        result_group = QGroupBox('Результат вычисления')
        result_layout = QVBoxLayout(result_group)
        self.result = QLabel('Здесь появится результат')
        self.result.setAlignment(Qt.AlignCenter)
        self.result.setWordWrap(True)
        self.result.setStyleSheet('font-size: 19px; font-weight: bold; color: #047857;')
        result_layout.addWidget(self.result)
        calc_layout.addWidget(result_group)
        calc_layout.addStretch()
        self.first.returnPressed.connect(self.calculate)
        self.second.returnPressed.connect(self.calculate)
        self.tabs.addTab(calc_tab, 'Калькулятор')

        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        self.history = QTableWidget(0, 5)
        self.history.setHorizontalHeaderLabels(['ID', 'Дата и время', 'Первое число', 'Операция', 'Второе число = Результат'])
        self.history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history.setSelectionMode(QAbstractItemView.SingleSelection)
        self.history.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.history.doubleClicked.connect(self.load_selected)
        history_layout.addWidget(self.history)
        history_buttons = QHBoxLayout()
        reload_button = QPushButton('Обновить')
        reload_button.clicked.connect(self.refresh_history)
        load_button = QPushButton('Загрузить в калькулятор')
        load_button.clicked.connect(self.load_selected)
        delete_button = QPushButton('Удалить запись')
        delete_button.clicked.connect(self.delete_selected)
        clear_history_button = QPushButton('Очистить историю')
        clear_history_button.setObjectName('danger')
        clear_history_button.clicked.connect(self.clear_history)
        for button in (reload_button, load_button, delete_button, clear_history_button):
            history_buttons.addWidget(button)
        history_layout.addLayout(history_buttons)
        self.tabs.addTab(history_tab, 'История SQL')

    def calculate(self):
        try:
            a = float(self.first.text().strip().replace(',', '.'))
            b = float(self.second.text().strip().replace(',', '.'))
            if not math.isfinite(a) or not math.isfinite(b):
                raise ValueError('Введите конечные числа.')
        except ValueError:
            QMessageBox.warning(self, 'Ошибка ввода', 'Введите корректные конечные числа в оба поля.\nПример: 12.5 или 12,5')
            return
        try:
            index = self.operation.currentIndex()
            if index == 0:
                value, sign = a + b, '+'
            elif index == 1:
                value, sign = a - b, '−'
            elif index == 2:
                value, sign = a * b, '×'
            elif index == 3:
                if b == 0:
                    raise ZeroDivisionError('Делить на ноль нельзя!')
                value, sign = a / b, '÷'
            else:
                value, sign = a ** b, '^'
                if isinstance(value, complex):
                    raise ValueError('Результат является комплексным числом.')
            if not math.isfinite(value):
                raise OverflowError('Результат выходит за допустимый диапазон.')
            self.result.setText(f'{a:g} {sign} {b:g} = {value:.10g}')
        except (OverflowError, ValueError, ZeroDivisionError) as error:
            QMessageBox.critical(self, 'Ошибка вычисления', str(error))
            return
        try:
            self.db.add(a, b, index, sign, value)
            self.refresh_history()
        except sqlite3.Error as error:
            QMessageBox.warning(self, 'Ошибка SQL', f'Результат вычислен, но не сохранён:\n{error}')

    def refresh_history(self):
        try:
            self.records = self.db.all()
        except sqlite3.Error as error:
            QMessageBox.critical(self, 'Ошибка SQL', str(error))
            return
        self.history.setRowCount(len(self.records))
        for row_index, (record_id, created, a, sign, b, result, operation_index) in enumerate(self.records):
            values = [str(record_id), created, f'{a:g}', sign, f'{b:g} = {result:.10g}']
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.history.setItem(row_index, column, item)

    def selected_record(self):
        row = self.history.currentRow()
        if row < 0 or row >= len(self.records):
            QMessageBox.information(self, 'История', 'Выберите строку в таблице.')
            return None
        return self.records[row]

    def load_selected(self, *_):
        record = self.selected_record()
        if record is None:
            return
        _, _, a, _, b, _, index = record
        self.first.setText(str(a))
        self.second.setText(str(b))
        self.operation.setCurrentIndex(index)
        self.result.setText('Нажмите «Вычислить» для повторного расчёта')
        self.tabs.setCurrentIndex(0)

    def delete_selected(self):
        record = self.selected_record()
        if record is None:
            return
        try:
            self.db.delete(record[0])
            self.refresh_history()
        except sqlite3.Error as error:
            QMessageBox.critical(self, 'Ошибка SQL', str(error))

    def clear_history(self):
        if not self.records:
            return
        answer = QMessageBox.question(self, 'Подтверждение', 'Удалить всю историю вычислений?',
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer == QMessageBox.Yes:
            try:
                self.db.clear()
                self.refresh_history()
            except sqlite3.Error as error:
                QMessageBox.critical(self, 'Ошибка SQL', str(error))

    def clear_fields(self):
        self.first.clear()
        self.second.clear()
        self.operation.setCurrentIndex(0)
        self.result.setText('Здесь появится результат')
        self.first.setFocus()

    def show_about(self):
        QMessageBox.information(self, 'О программе',
            'Универсальный калькулятор на Python и PyQt5.\n'
            'Пять математических операций, проверка ввода и обработка ошибок.\n'
            'История вычислений хранится в локальной базе данных SQLite.')

    def closeEvent(self, event):
        self.db.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec_())
