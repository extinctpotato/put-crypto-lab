import sys, argparse, logging
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
# In-tree modules
import aes, bbs_generator
from fips import run_all_tests as run_all_fips_tests
from aes import (
        test_lib as aes_test_lib, 
        LOGGER_ID as AES_LOGGER_ID,
        aesECB,
        aesCBC,
        aesOFB,
        )
from aes_tests import (
        ARISTOTLE_QUOTE as QUOTE, 
        run_all_tests as run_all_aes_mangle_tests
        )
from rsa import generate_rsa_keypair, rsa_encrypt_str, rsa_decrypt_str

l = logging.getLogger()

def __aes_X_enc_test_func(aes_impl, arg):
    plaintext = arg.plaintext.encode()
    a = aes_impl()

    # Join yielded blocks into 'bytes'.
    ciphertext = b"".join(
            list(a.encrypt(plaintext))
            )

    # Decrypt ciphertext and unpad it according to
    # AES block size.
    plaintext_restored = unpad(
            b"".join(
                list(a.decrypt(ciphertext))
                ),
            AES.block_size
            )

    l.info(plaintext_restored.decode())

def aes_ecb_enc_test_func(arg):
    __aes_X_enc_test_func(aesECB, arg)

def aes_cbc_enc_test_func(arg):
    __aes_X_enc_test_func(aesCBC, arg)

def aes_ofb_enc_test_func(arg):
    __aes_X_enc_test_func(aesOFB, arg)

def aes_test_lib_func(arg):
    aes_test_lib()

def rsa_enc_test_func(arg):
    e, d, n = generate_rsa_keypair()
    encrypted = rsa_encrypt_str(arg.plaintext, e, n)
    decrypted = rsa_decrypt_str(encrypted, len(arg.plaintext), d, n)

    l.info(f'e: {e}, d: {d}, n: {n}')
    l.info(decrypted)

def rsa_sign_test_func(arg):
    # Tuple elements are (e, d, n)
    #                    [0][1][2]
    keypair_a = generate_rsa_keypair()
    keypair_b = generate_rsa_keypair()

    l.info(f'keypair A: {keypair_a}')
    l.info(f'keypair B: {keypair_b}')

    # To sign a message, is to encrypt it 
    # using the private part instead of the public part.
    signed_with_a = rsa_encrypt_str(
            msg=arg.plaintext, 
            e=keypair_a[1],
            n=keypair_a[2],
            )
    signed_with_b = rsa_encrypt_str(
            msg=arg.plaintext,
            e=keypair_b[1],
            n=keypair_b[2],
            )

    # Just as in the previous case,
    # decryption is reversed as well,
    # so we decrypt using the public part.
    decrypted_a = rsa_decrypt_str(
            ciphertext=signed_with_a,
            msg_len=len(arg.plaintext),
            d=keypair_a[0],
            n=keypair_a[2],
            )
    decrypted_b = rsa_decrypt_str(
            ciphertext=signed_with_b,
            msg_len=len(arg.plaintext),
            d=keypair_b[0],
            n=keypair_b[2],
            )

    # Let's see what happens if we try to decrypt with a wrong key.
    decrypted_a_with_b = rsa_decrypt_str(
            ciphertext=signed_with_a,
            msg_len=len(arg.plaintext),
            d=keypair_b[0],
            n=keypair_b[2],
            )
    decrypted_b_with_a = rsa_decrypt_str(
            ciphertext=signed_with_b,
            msg_len=len(arg.plaintext),
            d=keypair_a[0],
            n=keypair_a[2],
            )

    l.info(f'A: {decrypted_a}')
    l.info(f'B: {decrypted_b}')
    l.info(f'A (with public B): {decrypted_a_with_b}')
    l.info(f'B (with public A): {decrypted_b_with_a}')

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

    aes_test_lib_arg = subparsers.add_parser("aes_test_lib")
    aes_test_lib_arg.set_defaults(func=aes_test_lib_func)

    aes_ecb_enc_test_arg = subparsers.add_parser("aes_ecb_enc_test")
    aes_ecb_enc_test_arg.add_argument("--plaintext", type=str, default=QUOTE)
    aes_ecb_enc_test_arg.set_defaults(func=aes_ecb_enc_test_func)

    aes_cbc_enc_test_arg = subparsers.add_parser("aes_cbc_enc_test")
    aes_cbc_enc_test_arg.add_argument("--plaintext", type=str, default=QUOTE)
    aes_cbc_enc_test_arg.set_defaults(func=aes_cbc_enc_test_func)

    aes_cbc_enc_test_arg = subparsers.add_parser("aes_ofb_enc_test")
    aes_cbc_enc_test_arg.add_argument("--plaintext", type=str, default=QUOTE)
    aes_cbc_enc_test_arg.set_defaults(func=aes_ofb_enc_test_func)

    rsa_enc_test_arg = subparsers.add_parser("rsa_enc_test")
    rsa_enc_test_arg.add_argument("--plaintext", type=str, default=QUOTE[:50])
    rsa_enc_test_arg.set_defaults(func=rsa_enc_test_func)

    rsa_sign_test_arg = subparsers.add_parser("rsa_sign_test")
    rsa_sign_test_arg.add_argument("--plaintext", type=str, default=QUOTE[:20])
    rsa_sign_test_arg.set_defaults(func=rsa_sign_test_func)

    aes_mangle_tests_arg = subparsers.add_parser("aes_mangle_tests")
    aes_mangle_tests_arg.add_argument("--mode", type=str, default="aesCBC")
    aes_mangle_tests_arg.set_defaults(
            func=lambda arg: run_all_aes_mangle_tests(getattr(aes, arg.mode))
            )

    generate_rsa_keypair_arg = subparsers.add_parser("generate_rsa_keypair")
    generate_rsa_keypair_arg.set_defaults(
            func=lambda arg: l.info(generate_rsa_keypair())
            )

    return parser

if __name__ == '__main__':
    logging.basicConfig(format="%(message)s")
    l.setLevel(logging.INFO)

    logging.getLogger(AES_LOGGER_ID).setLevel(logging.INFO)

    parser = get_parser()

    if (len(sys.argv) == 1):
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    
    res = args.func(args)

    if res == False:
        sys.exit(1)
