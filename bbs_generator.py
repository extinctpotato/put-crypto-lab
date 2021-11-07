from math import gcd
from random import randint

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
    p = 431
    q = 347
    n = p*q
    a = pick_random_a(n)
    r = 20

    print(f'n: {n}, a: {a}')

    assert valid_for_blum(p)
    assert valid_for_blum(q)

    return bbs(n, r, a)

if __name__ == '__main__':
    print(bbs_preset())
