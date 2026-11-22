

import math


class Calculator:
    def __init__(self):
        self.memory = 0.0
        self.history = []

    def _log(self, expression, result):
        self.history.append(f"{expression} = {result}")
        return result

    def add(self, a, b):
        return self._log(f"{a} + {b}", a + b)

    def subtract(self, a, b):
        return self._log(f"{a} - {b}", a - b)

    def multiply(self, a, b):
        return self._log(f"{a} * {b}", a * b)

    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError("Деление на ноль")
        return self._log(f"{a} / {b}", a / b)

    def memory_store(self, value):
        self.memory = value

    def memory_recall(self):
        return self.memory

    def memory_clear(self):
        self.memory = 0.0

    def show_history(self):
        return self.history


class EngineeringCalculator(Calculator):
    def power(self, base, exponent):
        return self._log(f"{base} ^ {exponent}", math.pow(base, exponent))

    def sqrt(self, x):
        if x < 0:
            raise ValueError("Корень из отрицательного числа")
        return self._log(f"sqrt({x})", math.sqrt(x))

    def nth_root(self, x, n):
        if x < 0 and n % 2 == 0:
            raise ValueError("Чётный корень из отрицательного числа")
        result = math.copysign(abs(x) ** (1 / n), x)
        return self._log(f"root({x}, {n})", result)

    def factorial(self, n):
        if n < 0 or int(n) != n:
            raise ValueError("Факториал определён только для неотрицательных целых")
        return self._log(f"{n}!", math.factorial(int(n)))

    def log10(self, x):
        return self._log(f"log10({x})", math.log10(x))

    def ln(self, x):
        return self._log(f"ln({x})", math.log(x))

    def log_base(self, x, base):
        return self._log(f"log_{base}({x})", math.log(x, base))

    def sin(self, x, degrees=True):
        value = math.radians(x) if degrees else x
        return self._log(f"sin({x})", math.sin(value))

    def cos(self, x, degrees=True):
        value = math.radians(x) if degrees else x
        return self._log(f"cos({x})", math.cos(value))

    def tan(self, x, degrees=True):
        value = math.radians(x) if degrees else x
        return self._log(f"tan({x})", math.tan(value))

    def asin(self, x, degrees=True):
        result = math.asin(x)
        return self._log(f"asin({x})", math.degrees(result) if degrees else result)

    def acos(self, x, degrees=True):
        result = math.acos(x)
        return self._log(f"acos({x})", math.degrees(result) if degrees else result)

    def atan(self, x, degrees=True):
        result = math.atan(x)
        return self._log(f"atan({x})", math.degrees(result) if degrees else result)

    def exp(self, x):
        return self._log(f"e^{x}", math.exp(x))

    def percent(self, value, percent):
        return self._log(f"{percent}% of {value}", value * percent / 100)


class CalculatorCLI:
    def __init__(self):
        self.calc = EngineeringCalculator()
        self.operations = {
            "1": ("Сложение", self._add),
            "2": ("Вычитание", self._subtract),
            "3": ("Умножение", self._multiply),
            "4": ("Деление", self._divide),
            "5": ("Степень", self._power),
            "6": ("Квадратный корень", self._sqrt),
            "7": ("Корень n-й степени", self._nth_root),
            "8": ("Факториал", self._factorial),
            "9": ("Логарифм по основанию 10", self._log10),
            "10": ("Натуральный логарифм", self._ln),
            "11": ("Логарифм по произвольному основанию", self._log_base),
            "12": ("Синус", self._sin),
            "13": ("Косинус", self._cos),
            "14": ("Тангенс", self._tan),
            "15": ("Арксинус", self._asin),
            "16": ("Арккосинус", self._acos),
            "17": ("Арктангенс", self._atan),
            "18": ("Экспонента e^x", self._exp),
            "19": ("Процент", self._percent),
            "20": ("Сохранить в память", self._mem_store),
            "21": ("Вызвать из памяти", self._mem_recall),
            "22": ("Очистить память", self._mem_clear),
            "23": ("История вычислений", self._history),
        }

    def _input_number(self, prompt):
        return float(input(prompt))

    def _add(self):
        a = self._input_number("a: ")
        b = self._input_number("b: ")
        print(self.calc.add(a, b))

    def _subtract(self):
        a = self._input_number("a: ")
        b = self._input_number("b: ")
        print(self.calc.subtract(a, b))

    def _multiply(self):
        a = self._input_number("a: ")
        b = self._input_number("b: ")
        print(self.calc.multiply(a, b))

    def _divide(self):
        a = self._input_number("a: ")
        b = self._input_number("b: ")
        print(self.calc.divide(a, b))

    def _power(self):
        base = self._input_number("основание: ")
        exponent = self._input_number("степень: ")
        print(self.calc.power(base, exponent))

    def _sqrt(self):
        x = self._input_number("x: ")
        print(self.calc.sqrt(x))

    def _nth_root(self):
        x = self._input_number("x: ")
        n = self._input_number("n: ")
        print(self.calc.nth_root(x, n))

    def _factorial(self):
        n = self._input_number("n: ")
        print(self.calc.factorial(n))

    def _log10(self):
        x = self._input_number("x: ")
        print(self.calc.log10(x))

    def _ln(self):
        x = self._input_number("x: ")
        print(self.calc.ln(x))

    def _log_base(self):
        x = self._input_number("x: ")
        base = self._input_number("основание: ")
        print(self.calc.log_base(x, base))

    def _sin(self):
        x = self._input_number("угол (градусы): ")
        print(self.calc.sin(x))

    def _cos(self):
        x = self._input_number("угол (градусы): ")
        print(self.calc.cos(x))

    def _tan(self):
        x = self._input_number("угол (градусы): ")
        print(self.calc.tan(x))

    def _asin(self):
        x = self._input_number("x: ")
        print(self.calc.asin(x))

    def _acos(self):
        x = self._input_number("x: ")
        print(self.calc.acos(x))

    def _atan(self):
        x = self._input_number("x: ")
        print(self.calc.atan(x))

    def _exp(self):
        x = self._input_number("x: ")
        print(self.calc.exp(x))

    def _percent(self):
        value = self._input_number("значение: ")
        percent = self._input_number("процент: ")
        print(self.calc.percent(value, percent))

    def _mem_store(self):
        value = self._input_number("значение для сохранения: ")
        self.calc.memory_store(value)

    def _mem_recall(self):
        print(self.calc.memory_recall())

    def _mem_clear(self):
        self.calc.memory_clear()

    def _history(self):
        for entry in self.calc.show_history():
            print(entry)

    def _print_menu(self):
        print("\n=== Инженерный калькулятор ===")
        for key, (label, _) in self.operations.items():
            print(f"{key}. {label}")
        print("0. Выход")

    def run(self):
        while True:
            self._print_menu()
            choice = input("Выбор: ").strip()
            if choice == "0":
                break
            action = self.operations.get(choice)
            if action is None:
                print("Неверный выбор")
                continue
            try:
                action[1]()
            except Exception as error:
                print(f"Ошибка: {error}")


if __name__ == "__main__":
    CalculatorCLI().run()