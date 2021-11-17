import sys, argparse, logging
import bbs_generator
from fips import run_all_tests as run_all_fips_tests

l = logging.getLogger()

def bbs_preset_func(arg):
    run_all_fips_tests(bbs_generator.bbs_preset(n=arg.n, a=arg.a))

def test_file_func(arg):
    with open(f'{arg.input_file}', 'r') as f:
        bin_list = list(map(int, list(f.read().strip().replace('\n', ''))))

    expected_len = 20000

    bin_list = bin_list[:expected_len]

    l.info(f'len: {len(bin_list)}')

    if len(bin_list) != expected_len:
        l.error(f'A string that will truncate to at least {expected_len} expected')
        return False

    return run_all_fips_tests(bin_list)


def make_and_encrypt_func(arg):
    assert bbs_generator.valid_for_blum(arg.p)
    assert bbs_generator.valid_for_blum(arg.q)

    with open(arg.input_file, 'r') as f:
        input_str = f.read()

    n = arg.p*arg.q
    a = bbs_generator.pick_random_a(n)
    message = bbs_generator.string_to_bin_list(input_str)

    key = bbs_generator.bbs(n=n, r=len(message), a=a)

    assert len(key) == len(message)

    if arg.input_file != '/dev/stdin':
        key_file_name = f'{arg.input_file}.bbs_key'
        ciphered_file_name = f'{arg.input_file}.bbs'

        with open(f'{arg.input_file}.bin_int', 'w') as f:
            f.write("".join(map(str, message)))
    else:
        key_file_name = 'key.bbs_key'
        ciphered_file_name = '/dev/stdout'

    with open(key_file_name, 'w') as f:
        f.write("".join(map(str, key)))

    ciphered = bbs_generator.otp(message, key)

    with open(ciphered_file_name, 'w') as f:
        f.write("".join(map(str, ciphered)))

def decrypt_func(arg):
    with open(arg.ciphered_file, 'r') as f:
        ciphered = list(map(int, list(f.read().strip().replace('\n', ''))))

    with open(arg.key_file, 'r') as f:
        key = list(map(int, list(f.read().strip().replace('\n', ''))))

    deciphered = bbs_generator.otp(ciphered, key)

    output_file = '/dev/stdout'

    with open(output_file, 'w') as f:
        f.write(bbs_generator.bin_list_to_string(deciphered))

def gen_bbs_func(arg):
    n = arg.p * arg.q
    a = bbs_generator.pick_random_a(n)
    r = bbs_generator.bbs(n=n, r=arg.r, a=a)

    with open('/dev/stdout', 'w') as f:
        f.write("".join(map(str, r)))

def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    bbs_preset_arg = subparsers.add_parser("bbs_preset")
    bbs_preset_arg.add_argument("--n", type=int, default=None)
    bbs_preset_arg.add_argument("--a", type=int, default=None)
    bbs_preset_arg.set_defaults(func=bbs_preset_func)

    make_and_encrypt_arg = subparsers.add_parser("make_and_encrypt")
    make_and_encrypt_arg.add_argument("input_file", type=str)
    make_and_encrypt_arg.add_argument("--p", type=int, default=bbs_generator.PRESET_P)
    make_and_encrypt_arg.add_argument("--q", type=int, default=bbs_generator.PRESET_Q)
    make_and_encrypt_arg.set_defaults(func=make_and_encrypt_func)

    decrypt_arg = subparsers.add_parser("decrypt")
    decrypt_arg.add_argument("ciphered_file", type=str)
    decrypt_arg.add_argument("key_file", type=str)
    decrypt_arg.set_defaults(func=decrypt_func)

    gen_bbs_arg = subparsers.add_parser("gen_bbs")
    gen_bbs_arg.add_argument("--p", type=int, default=bbs_generator.PRESET_P)
    gen_bbs_arg.add_argument("--q", type=int, default=bbs_generator.PRESET_Q)
    gen_bbs_arg.add_argument("--r", type=int, default=1000000)
    gen_bbs_arg.set_defaults(func=gen_bbs_func)

    test_file_arg = subparsers.add_parser("test_file")
    test_file_arg.add_argument("input_file", type=str)
    test_file_arg.set_defaults(func=test_file_func)

    return parser

if __name__ == '__main__':
    logging.basicConfig(format="%(message)s")
    l.setLevel(logging.INFO)

    parser = get_parser()

    if (len(sys.argv) == 1):
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    
    res = args.func(args)

    if res == False:
        sys.exit(1)
