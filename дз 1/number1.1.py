# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

a = int(input())
b = int(input())
s = input()
if s == '*':
    print(a * b)
elif s == '+':
    print(a + b)
elif s == '-':
    print(a - b)
else:
    if b == 0:
        print('ERROR')
    else: 
        print(a/b)
