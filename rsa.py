from sympy import randprime
# In-tree imports
from bbs_generator import is_congruent

def xea(a, b, s1=1, s2=0, t1=0, t2=1):
    q = a // b
    r = a % b

    s3 = s1 - q*s2
    t3 = t1 - q*t2

    if r == 0:
        return b, s2, t2

    return xea(b, r, s2, s3, t2, t3)

def gcd(a, b):
    if a == 0:
        return b
    elif b == 0:
        return a

    remainder = a % b

    return gcd(b, remainder)

def generate_rsa_keypair():
    # Prime numbers 'p' and 'q' must be irrecoverably
    # discarded after performing all calculations.
    p = randprime(0, 1000)
    q = randprime(0, 1000)

    # The 'n' product is used both for private and public key.
    n = p*q

    totient = (p-1)*(q-1)

    while gcd((e := randprime(0, totient)), totient) != 1:
        pass
