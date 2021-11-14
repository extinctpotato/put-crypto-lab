import sys, argparse
import bbs_generator
from fips import run_all_tests as run_all_fips_tests

def bbs_preset_func(arg):
    run_all_fips_tests(bbs_generator.bbs_preset())

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

    output_file = '/dev/stdout'

    deciphered = bbs_generator.otp(ciphered, key)

    with open(output_file, 'w') as f:
        f.write("".join(map(str, deciphered)))

def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    bbs_preset_arg = subparsers.add_parser("bbs_preset")
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

    return parser

if __name__ == '__main__':
    parser = get_parser()

    if (len(sys.argv) == 1):
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)
