

def lv2(t, m):
    if m == 'find':
        t_f = t.find('круто')
        return t_f
    if m == 'replace':
        t_r = t.replace('круто', 'тупо')
        return t_r
    if m == 'count':
        t_c = t.count('круто')
        return t_c
    
t = input()
m = input()
print(lv2(t, m))