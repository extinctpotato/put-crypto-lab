from math import gcd
from random import randint

class FIPS:
    def __init__(self, r):
        self.r = r

        if len(r) < 20000:
            print(r)

        #assert len(r) == 20000

    def single_bits_test(self):
        one_count = self.r.count(1)

        return one_count > 9725 and one_count < 10275

    def series_test(self):
        constraints = {
                1: (2315, 2685),
                2: (1114,1386),
                3: (527,723),
                4: (240,384),
                5: (103,209),
                6: (103,209)
                }

        one_ctr = 0
        zero_ctr = 0

        #     series: 0,1
        results = {k:[0,0] for k in range(1,7)}

        for b in self.r:
            if b == 0:
                if one_ctr > 1:
                    results[one_ctr-1][1] += 1

                # Reset 1-series counter
                one_ctr = 0

                if zero_ctr < 7:
                    zero_ctr += 1

            elif b == 1:
                if zero_ctr > 1:
                    results[zero_ctr-1][0] += 1

                # Reset 0-series counter
                zero_ctr = 0

                # Increment if not counting 0-series
                if one_ctr < 7:
                    one_ctr += 1

        print(results)

        return True

def run_all_tests(r):
    tests = [str(t) for t in dir(FIPS) if t.endswith("_test")]

    for t in tests:
        res = eval(f'FIPS({r}).{t}()')
        print(f'{t}: {res}')

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
    p = 30000000091
    q = 40000000003
    n = p*q
    a = pick_random_a(n)
    #r = 20000
    r = 10

    print(f'n: {n}, a: {a}')

    assert valid_for_blum(p)
    assert valid_for_blum(q)

    return bbs(n, r, a)

if __name__ == '__main__':
    #print(bbs_preset())
    r = bbs_preset()

    run_all_tests(r)
