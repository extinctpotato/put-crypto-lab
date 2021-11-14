from random import randint
from math import gcd
from fips import FIPS

PRESET_P = 30000000091
PRESET_Q = 40000000003

def is_congruent(a, b, n):
    return a%n == b%n

def valid_for_blum(a):
    return is_congruent(a, 3, 4)

def pick_random_a(n):
    a = n
    while gcd(a, n) != 1:
        a = randint(n, n*2)

    return a

def bbs(n, r, a):
    x = [pow(a, 2) % n]

    b = []

    for i in range(1, r+1):
        x_tmp = pow(x[i-1], 2) % n
        x.append(x_tmp)

        b.append(x_tmp % 2)

    return b

def bbs_preset():
    p = PRESET_P 
    q = PRESET_Q
    n = p*q
    a = pick_random_a(n)
    r = 20000
    #r = 10

    print(f'n: {n}, a: {a}')

    assert valid_for_blum(p)
    assert valid_for_blum(q)

    return bbs(n, r, a)

def otp(message, key):
    return [int(bool(m) ^ bool(k)) for m, k in zip(message, key)]

def string_otp(message_str, key):
    bin = lambda i: format(i, 'b')

    message = []

    for bin_int in map(bin, bytearray(message_str, encoding='utf8')):
        message.extend(list(bin_int))

    return otp(message, key)
