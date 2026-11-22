def lv4(t, m):
    if m == 'isdigit':
        t_id = t.isdigit()
        return t_id
    if m == 'isalpha':
        t_ia = t.isalpha()
        return t_ia
    if m == 'strip':
        t_st = t.strip()
        return t_st
    if m == 'lstrip':
        t_lst = t.lstrip()
        return t_lst
    if m == 'rstrip':
        t_rst = t.rstrip()
        return t_rst
    if m == 'format':
        t_for = t.format()
        return t_for

t = input()
m = input()