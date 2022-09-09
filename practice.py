#!/usr/bin/python3

# https://medium.com/co-learning-lounge/recursive-function-python-practice-examples-c37df75555e8
# get factorials
x = -1
def factorial(n):
    if n == 1:
        return 1
    else:
        return n*factorial(n-1)

# fibonacci sequence
def fibonacci(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def sumdigits(d):
    d = str(d)
    if len(d) == 1:
        return int(d)
    else:
        return int(d[0]) + sumdigits(int(d[1:]))
#x = sumdigits(142)

def sumnums(d):
    if d == 1:
        return 1
    else:
        return d + sumnums(d-1)
#x = sumnums(10)

def pow(b, e):
    if e == 0:
        return 1
    elif e == 1:
        return b
    else:
        return b * pow(b, e-1)
#x = pow(2, 3)



print(x)