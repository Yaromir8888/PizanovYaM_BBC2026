

def lv1(t, m):
    if m == 'upper':
        t_upp = t.upper()
        return t_upp
    if m == 'lower':
        t_low = t.lower()
        return t_low
    if m == 'capitalize':
        t_cap = t.capitalize()
        return t_cap
    
t = input()
m = input()
print(lv1(t, m))