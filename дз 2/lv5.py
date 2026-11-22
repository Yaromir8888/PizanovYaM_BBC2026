

def lv1(t, m):
    if m == 'upper':
        return t.upper()

    if m == 'lower':
        return t.lower()

    if m == 'capitalize':
        return t.capitalize()


def lv2(t, m):
    if m == 'find':
        return t.find('круто')

    if m == 'replace':
        return t.replace('круто', 'тупо')

    if m == 'count':
        return t.count('круто')


def lv3(t, m):
    if m == 'split':
        return t.split()

    if m == 'split join':
        return ''.join(t.split())

    if m == 'join':
        return ''.join(t)


def lv4(t, m):
    if m == 'isdigit':
        return t.isdigit()

    if m == 'isalpha':
        return t.isalpha()

    if m == 'strip':
        return t.strip()

    if m == 'lstrip':
        return t.lstrip()

    if m == 'rstrip':
        return t.rstrip()

    if m == 'format':
        return t.format()


def apply_method(t, m):
    if m in ['upper', 'lower', 'capitalize']:
        return lv1(t, m)

    if m in ['find', 'replace', 'count']:
        return lv2(t, m)

    if m in ['split', 'split join', 'join']:
        return lv3(t, m)

    if m in ['isdigit', 'isalpha', 'strip', 'lstrip', 'rstrip', 'format']:
        return lv4(t, m)

    print('Такого метода нет')
    return t


t = input('Введите строку: ')

print('Вводите методы по одному.')
print('Для окончания напишите stop.')

while True:
    m = input('Метод: ')

    if m == 'stop':
        break

    t = apply_method(t, m)
    print('Результат:', t)