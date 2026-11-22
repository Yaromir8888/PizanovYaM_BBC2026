#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 16:15:44 2026

@author: yaromirpizanov
"""

def pl(a, b, s):
   print(a + b)

def m(a, b, s):
    print(a - b)
        
def d(a, b, s):
    print(a * b)
    
def r(a, b, s):
    if b == 0:
        print('ERROR')
    else:
        print(a/b)
        
a = int(input())
b = int(input())
s = input()

if s == '*':
    d(a,b,s)
elif s == '+':
    pl(a,b,s)
elif s == '-':
    m(a,b,s)
else:
    r(a,b,s)
