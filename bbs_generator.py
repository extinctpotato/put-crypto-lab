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

def bbs_preset(n=None, a=None):
    p = PRESET_P 
    q = PRESET_Q
    n = n or p*q
    a = a or pick_random_a(n)
    r = 20000
    #r = 10

    print(f'n: {n}, a: {a}')

    assert valid_for_blum(p)
    assert valid_for_blum(q)

    return bbs(n, r, a)

def otp(message, key):
    return [int(bool(m) ^ bool(k)) for m, k in zip(message, key)]

def string_to_bin_list(message_str):
    bin = lambda i: format(i, '07b')

    message = []

    for bin_int in map(bin, bytearray(message_str, encoding='ascii')):
        message.extend(list(map(int, bin_int)))

    return message

def bin_list_to_string(message_lst):
    def __chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    s = bytearray('', encoding='ascii')

    for chunk in __chunks(message_lst, 7):
        s.append(int("".join(map(str, chunk)), 2))

    return s.decode()
