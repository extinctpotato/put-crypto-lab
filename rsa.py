from sympy import randprime
# In-tree imports
from bbs_generator import is_congruent

ENDIANNESS = 'little'

def int_to_base(n, b):
    if n == 0:
        return [0]

    digits = []

    while n:
        digits.append(int(n % b))
        n //= b

    return digits[::-1]

def base_to_int(n, b):
    r = range(0, len(n))
    i = 0

    for n_idx, b_idx in zip(r, reversed(r)):
        i += n[n_idx] * pow(b, b_idx)

    return i

def modular_multiplicative_inverse(a, m):
    _, t2, _ = xea(a, m)
    return t2 % m

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

    d = modular_multiplicative_inverse(
            a=e, 
            m=totient
            )

    return e, d, n

def rsa_encrypt(msg, e, n):
    return pow(msg, e) % n

def rsa_decrypt(ciphertext, d, n):
    return pow(ciphertext, d) % n

def rsa_encrypt_str(msg, e, n):
    msg_split = int_to_base(
            n=int.from_bytes(msg.encode(), ENDIANNESS),
            b=n
            )

    for msg_chunk in msg_split:
        yield rsa_encrypt(msg_chunk, e, n)

def rsa_decrypt_str(ciphertext, msg_len, d, n):
    msg_decrypted_chunks = []

    for ciphertext_chunk in ciphertext:
        msg_decrypted_chunks.append(
                rsa_decrypt(ciphertext_chunk, d, n)
                )

    msg_to_base10 = base_to_int(msg_decrypted_chunks, n)

    return int.to_bytes(msg_to_base10, msg_len, ENDIANNESS).decode()
