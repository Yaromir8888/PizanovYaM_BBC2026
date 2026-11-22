
def lv3(t, m):
    if m == 'split':
        t_sp = t.split()
        return t_sp
    if m == 'split join':
        t_sp = t.split(',')
        t_sj = ''.join(t_sp)
        return t_sj 
    if m == 'join':
        t_j = ''.join(t)
        return t_j 
    
t = input()
m = input()
print(lv3(t, m))