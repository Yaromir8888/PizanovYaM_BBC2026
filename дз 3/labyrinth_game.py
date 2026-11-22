"""Консольная игра «Лабиринт».

В игре намеренно используются основные операции со списками из задания:
append, extend, remove, pop, sort, reverse, in, index, copy, срезы,
copy.deepcopy и list comprehension.
Запуск: python3 labyrinth_game.py
"""

import random
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Optional


# ---------- Данные комнат и предметов ----------

@dataclass
class Room:
    kind: str = "empty"
    opened: bool = False          # сундук уже открыт
    cleared: bool = False         # монстр побеждён или ключ забран
    triggered: bool = False       # ловушка уже сработала
    loot: list = field(default_factory=list)
    monster_name: str = ""
    monster_hp: int = 0
    monster_damage: int = 0
    destination: Optional[tuple] = None
    floor_items: list = field(default_factory=list)  # предметы, выброшенные игроком


def make_item(name, item_type, **properties):
    """Создать предмет в виде словаря, который хранится внутри списка-инвентаря."""
    item = {"name": name, "type": item_type}
    item.update(properties)
    return item


def make_room(kind):
    """Сформировать комнату выбранного типа."""
    room = Room(kind=kind)

    if kind == "chest":
        # Сундук может быть пустым с вероятностью 35%.
        if random.random() >= 0.35:
            templates = [
                make_item("Зелье лечения", "зелье", heal=30),
                make_item("Кристалл маны", "материал"),
                make_item("Отмычки", "инструмент", disarm_bonus=20),
                make_item("Серебряный жетон", "ценность", value=1),
                make_item("Меч искателя", "оружие", damage=12, mana=0),
            ]
            count = random.randint(1, min(2, len(templates)))
            room.loot = deepcopy(random.sample(templates, count))

    elif kind == "monster":
        monsters = [
            ("Гоблин", 25, 7),
            ("Слизень", 20, 5),
            ("Скелет", 32, 8),
            ("Орк", 40, 10),
        ]
        room.monster_name, room.monster_hp, room.monster_damage = random.choice(monsters)

    return room


# ---------- Игра ----------

class LabyrinthGame:
    SYMBOLS = {
        "empty": ".",
        "chest": "C",
        "monster": "M",
        "trap": "T",
        "key": "K",
        "portal": "O",
        "exit": "E",
    }

    DIRECTIONS = {
        "w": (-1, 0),  # вверх
        "d": (0, 1),   # вправо
        "s": (1, 0),   # вниз
        "a": (0, -1),  # влево
    }

    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.start = (0, 0)
        self.exit_pos = (rows - 1, cols - 1)
        self.position = self.start

        # Два требуемых списка: матрица всех комнат и список посещённых координат.
        self.rooms = self.generate_rooms()
        self.visited_rooms = []

        self.max_hp = 100
        self.health_points = self.max_hp
        self.won = False
        self.game_over = False

        # Стартовый инвентарь — обычный список словарей.
        self.inventory = [
            make_item("Ржавый меч", "оружие", damage=8, mana=0),
            make_item("Зелье лечения", "зелье", heal=25),
        ]

        self.register_visit(self.position)

    def generate_rooms(self):
        """Создать матрицу комнат, гарантируя ключ, выход, два портала и опасности."""
        coordinates = [(x, y) for x in range(self.rows) for y in range(self.cols)]
        grid = [[Room() for _ in range(self.cols)] for _ in range(self.rows)]

        special = {self.start, self.exit_pos}
        available = [p for p in coordinates if p not in special]

        key_pos = random.choice(available)
        available.remove(key_pos)

        portal_positions = random.sample(available, 2)
        for p in portal_positions:
            available.remove(p)

        grid[key_pos[0]][key_pos[1]] = make_room("key")
        grid[self.exit_pos[0]][self.exit_pos[1]] = make_room("exit")

        first_portal, second_portal = portal_positions
        grid[first_portal[0]][first_portal[1]] = make_room("portal")
        grid[second_portal[0]][second_portal[1]] = make_room("portal")
        grid[first_portal[0]][first_portal[1]].destination = second_portal
        grid[second_portal[0]][second_portal[1]].destination = first_portal

        # В лабиринте гарантированно есть хотя бы один сундук, монстр и ловушка.
        random.shuffle(available)
        mandatory_types = ["chest", "monster", "trap"]
        for position, kind in zip(available[:3], mandatory_types):
            x, y = position
            grid[x][y] = make_room(kind)

        # Остальные комнаты генерируются случайно.
        for x, y in available[3:]:
            kind = random.choices(
                ["empty", "chest", "monster", "trap"],
                weights=[5, 2, 2, 1],
                k=1,
            )[0]
            grid[x][y] = make_room(kind)

        return grid

    # ---------- Общие вспомогательные функции ----------

    def register_visit(self, position):
        # Операция in проверяет, посещал ли игрок эту комнату раньше.
        if position not in self.visited_rooms:
            self.visited_rooms.append(position)  # append

    def current_room(self):
        x, y = self.position
        return self.rooms[x][y]

    @staticmethod
    def ask_yes_no(question):
        return input(question + " (д/н): ").strip().lower() in {"д", "да", "y", "yes"}

    @staticmethod
    def read_number(prompt, minimum, maximum):
        while True:
            answer = input(prompt).strip()
            try:
                value = int(answer)
            except ValueError:
                print("Введите целое число.")
                continue
            if minimum <= value <= maximum:
                return value
            print(f"Введите число от {minimum} до {maximum}.")

    def find_item_index(self, name):
        """Поиск предмета с использованием in и index."""
        item_names = [item["name"] for item in self.inventory]  # list comprehension
        if name in item_names:  # in
            return item_names.index(name)  # index
        return None

    def player_damage(self):
        # List comprehension выбирает оружие из инвентаря.
        weapons = [item for item in self.inventory if item.get("type") == "оружие"]
        return 5 + sum(item.get("damage", 0) for item in weapons)

    # ---------- Карта и состояние ----------

    def show_map(self):
        print("\nКарта (?: неизведанная комната, P: вы):")
        print("    " + " ".join(f"{y:2}" for y in range(self.cols)))
        for x in range(self.rows):
            cells = []
            for y in range(self.cols):
                position = (x, y)
                if position == self.position:
                    symbol = "P"
                elif position in self.visited_rooms:
                    symbol = self.SYMBOLS.get(self.rooms[x][y].kind, "?")
                else:
                    symbol = "?"
                cells.append(f"{symbol:>2}")
            print(f"{x:2}  " + " ".join(cells))
        print("Обозначения: . пустая, C сундук, M монстр, T ловушка, K ключ, O портал, E выход")

    def show_status(self):
        x, y = self.position
        print(f"\nЗдоровье: {self.health_points}/{self.max_hp} HP")
        print(f"Координаты: (x={x}, y={y})")
        print(f"Посещено комнат: {len(self.visited_rooms)} из {self.rows * self.cols}")
        print(f"Урон игрока: {self.player_damage()}")
        if self.find_item_index("Ключ от выхода") is not None:
            print("Ключ от выхода: есть")
        else:
            print("Ключ от выхода: нет")

    # ---------- Перемещение ----------

    def move(self):
        print("Направления: W — вверх, D — вправо, S — вниз, A — влево.")
        direction = input("Куда идти? ").strip().lower()
        if direction not in self.DIRECTIONS:
            print("Неизвестное направление.")
            return

        dx, dy = self.DIRECTIONS[direction]
        x, y = self.position
        new_position = (x + dx, y + dy)
        nx, ny = new_position

        # Проверка прямоугольных стен по периметру: выйти за матрицу нельзя.
        if not (0 <= nx < self.rows and 0 <= ny < self.cols):
            print("Там стена лабиринта. За пределы карты пройти нельзя.")
            return

        previous_position = self.position
        self.position = new_position
        self.register_visit(self.position)
        print(f"Вы перешли в комнату {self.position}.")
        self.enter_current_room(previous_position)

    # ---------- Комнаты ----------

    def enter_current_room(self, previous_position=None):
        room = self.current_room()

        if room.kind == "empty":
            print("Комната пуста. Можно двигаться дальше.")

        elif room.kind == "chest":
            if room.opened:
                print("Этот сундук уже открыт.")
            elif self.ask_yes_no("Вы нашли сундук. Открыть его?"):
                room.opened = True
                if not room.loot:
                    print("Сундук пуст!")
                else:
                    found_items = deepcopy(room.loot)
                    print("Найдено:", ", ".join(item["name"] for item in found_items))
                    self.inventory.extend(found_items)  # extend: добавить сразу несколько предметов
            else:
                print("Вы оставили сундук закрытым. Можно осмотреть комнату позже.")

        elif room.kind == "monster":
            if room.cleared:
                print("Здесь уже никого нет: монстр побеждён.")
            else:
                print(f"На вас нападает монстр: {room.monster_name}!")
                self.fight_monster(room, previous_position)

        elif room.kind == "trap":
            if room.triggered:
                print("Ловушка уже сработала и больше не опасна.")
            else:
                self.handle_trap(room)

        elif room.kind == "key":
            if room.cleared:
                print("Здесь вы уже забрали ключ.")
            else:
                key = make_item("Ключ от выхода", "ключ")
                self.inventory.append(key)  # append: добавить один предмет
                room.cleared = True
                print("Вы нашли ключ от выхода и положили его в инвентарь!")

        elif room.kind == "portal":
            self.handle_portal(room)

        elif room.kind == "exit":
            self.handle_exit()

    def handle_trap(self, room):
        print("Вы заметили ловушку на полу!")
        print("1. Попытаться обезвредить (60% успеха; отмычки повышают шанс на 20%).")
        print("2. Быстро пройти, рискуя получить урон.")
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            has_tools = any(item.get("name") == "Отмычки" for item in self.inventory)
            chance = 0.80 if has_tools else 0.60
            if random.random() < chance:
                print("Успех! Ловушка обезврежена.")
            else:
                damage = random.randint(10, 22)
                self.health_points -= damage
                print(f"Не получилось! Ловушка нанесла {damage} урона.")
        elif choice == "2":
            damage = random.randint(8, 18)
            self.health_points -= damage
            print(f"Вы проскочили, но получили {damage} урона.")
        else:
            print("Вы замешкались и задели ловушку.")
            damage = random.randint(8, 18)
            self.health_points -= damage
            print(f"Получено {damage} урона.")

        room.triggered = True
        self.check_health()

    def handle_portal(self, room):
        destination = room.destination
        if destination is None:
            print("Портал не работает.")
            return

        if self.ask_yes_no(f"Здесь портал в комнату {destination}. Перейти?"):
            self.position = destination
            self.register_visit(destination)
            print(f"Портал перенёс вас в комнату {destination}.")
            print("Выход из портала не активирован автоматически — это защищает от бесконечного переноса.")

    def handle_exit(self):
        key_index = self.find_item_index("Ключ от выхода")
        if key_index is None:
            print("Вы нашли выход, но дверь заперта. Нужен ключ.")
            return

        print("Вы нашли выход и у вас есть ключ!")
        if self.ask_yes_no("Использовать ключ и завершить игру?"):
            used_key = self.inventory.pop(key_index)  # pop: извлечь ключ из списка
            print(f"Вы использовали предмет «{used_key['name']}».")
            self.won = True
            print("Поздравляем! Вы выбрались из лабиринта.")

    # ---------- Бой ----------

    def fight_monster(self, room, previous_position):
        while room.monster_hp > 0 and self.health_points > 0:
            print(f"\n{room.monster_name}: {room.monster_hp} HP | Вы: {self.health_points}/{self.max_hp} HP")
            print("1. Атаковать")
            print("2. Использовать зелье лечения")
            print("3. Отступить")
            choice = input("Действие: ").strip()

            if choice == "1":
                damage = self.player_damage()
                room.monster_hp -= damage
                print(f"Вы нанесли {damage} урона.")
                if room.monster_hp <= 0:
                    room.cleared = True
                    print(f"Вы победили: {room.monster_name}!")
                    if random.random() < 0.65:
                        loot = make_item("Серебряный жетон", "ценность", value=1)
                        self.inventory.append(loot)
                        print("Монстр оставил предмет: Серебряный жетон.")
                    break

            elif choice == "2":
                if not self.use_potion():
                    continue

            elif choice == "3":
                if previous_position is None:
                    print("Отступить некуда.")
                    continue
                self.position = previous_position
                print(f"Вы отступили в комнату {self.position}.")
                return

            else:
                print("Выберите 1, 2 или 3.")
                continue

            if room.monster_hp > 0:
                self.health_points -= room.monster_damage
                print(f"{room.monster_name} наносит вам {room.monster_damage} урона.")
                self.check_health()

        if room.monster_hp <= 0:
            room.cleared = True

    def check_health(self):
        if self.health_points <= 0:
            self.health_points = 0
            self.game_over = True
            print("Вы потеряли все очки здоровья. Игра окончена.")

    # ---------- Инвентарь ----------

    def show_inventory(self):
        print("\n--- Инвентарь ---")
        if not self.inventory:
            print("Инвентарь пуст.")
            return
        for index, item in enumerate(self.inventory, start=1):
            properties = []
            if "damage" in item:
                properties.append(f"урон: {item['damage']}")
            if "mana" in item:
                properties.append(f"мана: {item['mana']}")
            if "heal" in item:
                properties.append(f"лечение: {item['heal']} HP")
            suffix = f" ({', '.join(properties)})" if properties else ""
            print(f"{index}. {item['name']} [{item['type']}]{suffix}")

        # Срез списка: выводим первые три предмета как отдельный список.
        first_three = self.inventory[:3]
        print("Первые предметы (срез inventory[:3]):", [item["name"] for item in first_three])

    def pick_up_floor_items(self):
        floor_items = self.current_room().floor_items
        if not floor_items:
            print("В этой комнате на полу нет предметов.")
            return

        print("На полу:", ", ".join(item["name"] for item in floor_items))
        if self.ask_yes_no("Подобрать все эти предметы?"):
            self.inventory.extend(deepcopy(floor_items))
            floor_items.clear()
            print("Предметы добавлены в инвентарь.")

    def drop_by_name(self):
        if not self.inventory:
            print("Инвентарь пуст.")
            return
        name = input("Введите точное название предмета: ").strip()
        index = self.find_item_index(name)
        if index is None:
            print("Такого предмета в инвентаре нет.")
            return

        item = self.inventory[index]
        self.inventory.remove(item)  # remove: удалить предмет по значению
        self.current_room().floor_items.append(item)
        print(f"Вы выбросили «{item['name']}» на пол. Его можно подобрать снова.")

    def drop_by_number(self):
        if not self.inventory:
            print("Инвентарь пуст.")
            return
        self.show_inventory()
        index = self.read_number("Номер предмета для выбрасывания: ", 1, len(self.inventory)) - 1
        item = self.inventory.pop(index)  # pop: удалить по позиции
        self.current_room().floor_items.append(item)
        print(f"Вы выбросили «{item['name']}» на пол.")

    def use_potion(self):
        potion_index = self.find_item_index("Зелье лечения")
        if potion_index is None:
            print("У вас нет зелья лечения.")
            return False

        potion = self.inventory.pop(potion_index)
        old_hp = self.health_points
        self.health_points = min(self.max_hp, self.health_points + potion.get("heal", 25))
        print(f"Зелье восстановило {self.health_points - old_hp} HP.")
        return True

    def upgrade_weapon(self):
        # list comprehension формирует список позиций всех видов оружия.
        weapon_slots = [i for i, item in enumerate(self.inventory) if item.get("type") == "оружие"]
        if not weapon_slots:
            print("У вас нет оружия для улучшения.")
            return

        crystal_index = self.find_item_index("Кристалл маны")
        if crystal_index is None:
            print("Нужен предмет «Кристалл маны». Ищите его в сундуках.")
            return

        print("Какое оружие улучшить? Кристалл добавит +10 маны и +10 к урону.")
        for number, slot in enumerate(weapon_slots, start=1):
            weapon = self.inventory[slot]
            print(f"{number}. {weapon['name']} (урон {weapon.get('damage', 0)})")
        choice = self.read_number("Номер оружия: ", 1, len(weapon_slots))
        weapon = self.inventory[weapon_slots[choice - 1]]
        weapon["damage"] = weapon.get("damage", 0) + 10
        weapon["mana"] = weapon.get("mana", 0) + 10
        self.inventory.pop(crystal_index)
        print(f"«{weapon['name']}» улучшен: урон {weapon['damage']}, мана {weapon['mana']}.")

    def sort_inventory(self):
        print("1. По типу, затем по названию")
        print("2. По названию")
        choice = input("Критерий сортировки: ").strip()
        if choice == "1":
            self.inventory.sort(key=lambda item: (item.get("type", ""), item.get("name", "").casefold()))
        elif choice == "2":
            self.inventory.sort(key=lambda item: item.get("name", "").casefold())
        else:
            print("Сортировка отменена.")
            return
        print("Инвентарь отсортирован методом sort().")
        self.show_inventory()

    def reverse_inventory(self):
        self.inventory.reverse()  # reverse: изменить порядок элементов на обратный
        print("Порядок предметов изменён на обратный методом reverse().")
        self.show_inventory()

    def search_item(self):
        if not self.inventory:
            print("Инвентарь пуст.")
            return
        name = input("Название предмета для поиска: ").strip()
        names = [item["name"] for item in self.inventory]
        if name in names:
            print(f"Предмет найден. Первая позиция в списке (index): {names.index(name) + 1}.")
        else:
            print("Такого предмета нет (проверка через in).")

    def show_copy_examples(self):
        """Показать разницу между поверхностным и глубоким копированием безопасно."""
        shallow_copy = self.inventory.copy()  # поверхностная копия списка
        inventory_slice = self.inventory[:3]  # срез
        deep_copy = deepcopy(self.inventory)  # глубокая копия вложенных словарей

        print("\nПримеры копирования:")
        print("Исходный список:", [item["name"] for item in self.inventory])
        print("inventory.copy():", [item["name"] for item in shallow_copy])
        print("inventory[:3]:", [item["name"] for item in inventory_slice])
        print("deepcopy(inventory):", [item["name"] for item in deep_copy])
        if self.inventory:
            print("shallow_copy[0] is inventory[0] ->", shallow_copy[0] is self.inventory[0])
            print("Это True: список новый, но вложенный словарь предмета общий.")

        # Маленький отдельный пример показывает эффект изменения вложенного объекта,
        # не повреждая реальный инвентарь игрока.
        example = [{"name": "Тестовый меч", "stats": {"damage": 10}}]
        shallow_example = example.copy()
        deep_example = deepcopy(example)
        shallow_example[0]["stats"]["damage"] += 1
        print("После изменения shallow-копии у оригинала урон:", example[0]["stats"]["damage"])
        example[0]["stats"]["damage"] = 10  # восстановление тестового значения
        deep_example[0]["stats"]["damage"] += 1
        print("После изменения deep-копии у оригинала урон:", example[0]["stats"]["damage"])

    def inventory_menu(self):
        while not self.game_over and not self.won:
            print("\n=== ИНВЕНТАРЬ ===")
            print("1. Посмотреть инвентарь")
            print("2. Подобрать предметы с пола в текущей комнате")
            print("3. Выбросить предмет по названию (remove)")
            print("4. Выбросить предмет по номеру (pop)")
            print("5. Использовать зелье лечения")
            print("6. Улучшить оружие кристаллом маны (+10 к урону)")
            print("7. Сортировать инвентарь (sort)")
            print("8. Развернуть порядок предметов (reverse)")
            print("9. Найти предмет (in и index)")
            print("10. Примеры copy, среза и deepcopy")
            print("0. Назад")
            choice = input("Выберите действие: ").strip()

            if choice == "1":
                self.show_inventory()
            elif choice == "2":
                self.pick_up_floor_items()
            elif choice == "3":
                self.drop_by_name()
            elif choice == "4":
                self.drop_by_number()
            elif choice == "5":
                self.use_potion()
            elif choice == "6":
                self.upgrade_weapon()
            elif choice == "7":
                self.sort_inventory()
            elif choice == "8":
                self.reverse_inventory()
            elif choice == "9":
                self.search_item()
            elif choice == "10":
                self.show_copy_examples()
            elif choice == "0":
                return
            else:
                print("Нет такого пункта меню.")

    # ---------- Основной цикл ----------

    def run(self):
        print("=" * 48)
        print("               ЛАБИРИНТ")
        print("=" * 48)
        print(f"Размер лабиринта: {self.rows} x {self.cols}")
        print("Вы начинаете в координатах (0, 0). Найдите ключ и доберитесь до выхода.")
        print("Карта скрывает неизведанные комнаты. За границу лабиринта пройти нельзя.")
        print("Управление: W — вверх, D — вправо, S — вниз, A — влево.")

        while not self.game_over and not self.won:
            print(f"\nВы в комнате {self.position}. HP: {self.health_points}/{self.max_hp}")
            print("1. Переместиться")
            print("2. Инвентарь")
            print("3. Показать карту")
            print("4. Осмотреть текущую комнату")
            print("5. Статус игрока")
            print("0. Завершить игру")
            choice = input("Ваш выбор: ").strip()

            if choice == "1":
                self.move()
            elif choice == "2":
                self.inventory_menu()
            elif choice == "3":
                self.show_map()
            elif choice == "4":
                self.enter_current_room()
            elif choice == "5":
                self.show_status()
            elif choice == "0":
                print("Вы завершили игру.")
                return
            else:
                print("Нет такого пункта меню.")

        if self.won:
            print("Спасибо за игру!")
        elif self.game_over:
            print("Попробуйте ещё раз: расположение комнат будет другим.")


def main():
    print("Создание лабиринта")
    rows = LabyrinthGame.read_number("Количество строк (от 3 до 10): ", 3, 10)
    cols = LabyrinthGame.read_number("Количество столбцов (от 3 до 10): ", 3, 10)
    game = LabyrinthGame(rows, cols)
    game.run()


if __name__ == "__main__":
    main()
