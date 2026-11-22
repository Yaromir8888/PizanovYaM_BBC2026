# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 15:35:31 2026

@author: m2613390
"""
def f(a, b, s):
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
while True:
    a = int(input())
    b = int(input())
    s = input()
    f(a,b,s)