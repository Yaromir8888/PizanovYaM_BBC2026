import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QComboBox,
    QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox)


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Универсальный калькулятор — PyQt6')
        self.resize(460, 350)
        self.create_ui()

    def create_ui(self):
        self.setStyleSheet('''
            QWidget { background: #f4f6fb; color: #1f2937; font-size: 14px; }
            QLineEdit, QComboBox { background: white; border: 1px solid #cbd5e1;
                border-radius: 7px; padding: 9px; min-height: 22px; }
            QLineEdit:focus, QComboBox:focus { border: 2px solid #2563eb; }
            QPushButton { background: #2563eb; color: white; border: none;
                border-radius: 7px; padding: 11px; font-weight: bold; }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton#clear { background: #64748b; }
            QPushButton#clear:hover { background: #475569; }
            QGroupBox { border: 1px solid #cbd5e1; border-radius: 9px;
                margin-top: 12px; padding: 15px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 5px; }
        ''')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(13)

        heading = QLabel('Универсальный калькулятор')
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        heading.setStyleSheet('font-size: 22px; font-weight: bold; color: #1e40af;')
        layout.addWidget(heading)
        description = QLabel('Введите два числа и выберите математическую операцию.')
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)

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
        layout.addLayout(form)

        buttons = QHBoxLayout()
        calculate = QPushButton('Вычислить')
        calculate.clicked.connect(self.calculate)
        clear = QPushButton('Очистить')
        clear.setObjectName('clear')
        clear.clicked.connect(self.clear_fields)
        about = QPushButton('О программе')
        about.clicked.connect(self.show_about)
        buttons.addWidget(calculate)
        buttons.addWidget(clear)
        buttons.addWidget(about)
        layout.addLayout(buttons)

        result_group = QGroupBox('Результат вычисления')
        result_layout = QVBoxLayout(result_group)
        self.result = QLabel('Здесь появится результат')
        self.result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result.setWordWrap(True)
        self.result.setStyleSheet('font-size: 19px; font-weight: bold; color: #047857;')
        result_layout.addWidget(self.result)
        layout.addWidget(result_group)
        self.first.returnPressed.connect(self.calculate)
        self.second.returnPressed.connect(self.calculate)

    def calculate(self):
        try:
            a = float(self.first.text().strip().replace(',', '.'))
            b = float(self.second.text().strip().replace(',', '.'))
        except ValueError:
            QMessageBox.warning(self, 'Ошибка ввода',
                                'Введите корректные числа в оба поля.\nПример: 12.5 или 12,5')
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
                    QMessageBox.critical(self, 'Ошибка вычисления', 'Делить на ноль нельзя!')
                    return
                value, sign = a / b, '÷'
            else:
                value, sign = a ** b, '^'
                if isinstance(value, complex):
                    raise ValueError('Результат является комплексным числом.')
            self.result.setText(f'{a:g} {sign} {b:g} = {value:.10g}')
        except (OverflowError, ValueError, ZeroDivisionError) as error:
            QMessageBox.critical(self, 'Ошибка вычисления', str(error))

    def clear_fields(self):
        self.first.clear()
        self.second.clear()
        self.operation.setCurrentIndex(0)
        self.result.setText('Здесь появится результат')
        self.first.setFocus()

    def show_about(self):
        QMessageBox.information(self, 'О программе',
            'Универсальный калькулятор на Python и PyQt6.\n'
            'Поддерживает пять математических операций, проверку ввода и обработку ошибок.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec())
