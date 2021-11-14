from math import gcd
from random import randint

class FIPS:
    def __init__(self, r):
        self.r = r

        if len(r) < 20000:
            print(self.r)

        #assert len(r) == 20000

    def __count_series(self, bit_array, max_len):
        series = [[0 for _ in range(0,max_len)] for _ in range(0,2)] 
        prev_num = None
        counter = [0,0]

        for b in bit_array:
            if b == prev_num or prev_num is None:
                counter[b] += 1
                if counter[b] > 6:
                    counter[b] = 6

            else:
                series[int(not b)][counter[int(not b)]-1] += 1
                counter[b] = 1

            prev_num = b

        series[prev_num][counter[prev_num]-1] += 1

        return series

    def single_bits_test(self):
        one_count = self.r.count(1)

        return one_count > 9725 and one_count < 10275

    def series_test(self):
        constraints = [
                (2315, 2685),
                (1114,1386),
                (527,723),
                (240,384),
                (103,209),
                (103,209)
                ]

        series = self.__count_series(self.r, 6)

        for single_series in series:
            for val, limits in zip(single_series, constraints):
                if not (limits[0] <= val <= limits[1]):
                    return False

        return True

    def long_series_test(self):
        series = self.__count_series(self.r, 26)

        for single_series in series:
            if single_series[25] > 0:
                return False

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
    r = 20000
    #r = 10

    print(f'n: {n}, a: {a}')

    assert valid_for_blum(p)
    assert valid_for_blum(q)

    return bbs(n, r, a)

if __name__ == '__main__':
    r = bbs_preset()

    run_all_tests(r)
