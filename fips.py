from math import gcd
from textwrap import wrap

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
                if counter[b] > max_len:
                    counter[b] = max_len

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

    def poker_test(self):
        # A list of padded binary numbers.
        binary_0_to_15 = ["{0:04b}".format(i) for i in range(0,16)]

        # Convert bitlist to a string and divide it to a list
        # of 4-character strings representing padded binary numbers.
        chunked = wrap("".join(map(str, self.r)), 4)

        occurences = [chunked.count(b) for b in binary_0_to_15]

        X = (sum([pow(i,2) for i in occurences]) * 16 / 5000) - 5000

        return 2.16 < X < 46.17

def run_all_tests(r):
    tests = [str(t) for t in dir(FIPS) if t.endswith("_test")]

    for t in tests:
        res = eval(f'FIPS({r}).{t}()')
        print(f'{t}: {res}')
